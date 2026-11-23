"""Compare Whisper sizes on both Portuguese synthetic reference consultations."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
sys.path.insert(0, str(CODE_DIR / "src"))

from fisio_fase4.audio_text import transcribe


def words(text):
    return re.findall(r"\w+", text.casefold())


def word_error(reference, hypothesis):
    previous = list(range(len(hypothesis) + 1))
    for index, expected in enumerate(reference, start=1):
        current = [index]
        for column, actual in enumerate(hypothesis, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[column] + 1,
                    previous[column - 1] + (expected != actual),
                )
            )
        previous = current
    edits = previous[-1]
    return edits, edits / max(1, len(reference))


def peak_rss_mib():
    try:
        import resource

        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # macOS reports bytes; Linux and other supported POSIX systems report KiB.
        return value / (1024**2) if sys.platform == "darwin" else value / 1024
    except (ImportError, AttributeError):
        return None


def run_one(consultation_id, model_name):
    source_dir = PROJECT_ROOT / "data/public/consultas"
    transcript_path = source_dir / f"{consultation_id}_transcript.json"
    audio_path = source_dir / f"{consultation_id}_consultation.wav"
    reference_segments = json.loads(transcript_path.read_text(encoding="utf-8"))
    reference = words(" ".join(segment["text"] for segment in reference_segments))
    started = time.perf_counter()
    result = transcribe(audio_path, model_name=model_name, language="pt")
    edits, wer = word_error(reference, words(result["text"]))
    return {
        "consultation": consultation_id,
        "model": model_name,
        "reference_words": len(reference),
        "edits": edits,
        "wer": round(wer, 4),
        "seconds": round(time.perf_counter() - started, 3),
        "peak_rss_mib": round(peak_rss_mib(), 1) if peak_rss_mib() is not None else None,
        "language_detected": result.get("language"),
        "status": "ok",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="+", choices=["OAW01", "OAW04"], default=["OAW01", "OAW04"])
    parser.add_argument("--models", nargs="+", choices=["tiny", "base", "small"], default=["tiny", "base", "small"])
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "docs/resultados/whisper_comparacao.json")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--worker-id", choices=["OAW01", "OAW04"], help=argparse.SUPPRESS)
    parser.add_argument("--worker-model", choices=["tiny", "base", "small"], help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.worker:
        try:
            result = run_one(args.worker_id, args.worker_model)
        except Exception as exc:
            result = {
                "consultation": args.worker_id,
                "model": args.worker_model,
                "status": "erro",
                "error": f"{type(exc).__name__}: {exc}",
            }
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["status"] == "ok" else 1

    rows = []
    for consultation_id in args.ids:
        for model_name in args.models:
            command = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                "--worker-id",
                consultation_id,
                "--worker-model",
                model_name,
            ]
            process = subprocess.run(command, capture_output=True, text=True)
            try:
                result = json.loads(process.stdout.strip().splitlines()[-1])
            except (IndexError, json.JSONDecodeError):
                result = {
                    "consultation": consultation_id,
                    "model": model_name,
                    "status": "erro",
                    "error": process.stderr[-2000:] or "Worker returned no result.",
                }
            rows.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)

    aggregate = {}
    for model_name in args.models:
        model_rows = [row for row in rows if row["model"] == model_name and row["status"] == "ok"]
        word_count = sum(row["reference_words"] for row in model_rows)
        edit_count = sum(row["edits"] for row in model_rows)
        aggregate[model_name] = {
            "successful_samples": len(model_rows),
            "total_samples": len(args.ids),
            "reference_words": word_count,
            "edits": edit_count,
            "aggregate_wer": round(edit_count / word_count, 4) if word_count else None,
            "total_seconds": round(sum(row["seconds"] for row in model_rows), 3),
            "mean_peak_rss_mib": round(
                sum(row["peak_rss_mib"] for row in model_rows if row["peak_rss_mib"] is not None)
                / max(1, sum(row["peak_rss_mib"] is not None for row in model_rows)),
                1,
            )
            if any(row["peak_rss_mib"] is not None for row in model_rows)
            else None,
        }
    valid = [
        (stats["aggregate_wer"], stats["total_seconds"], name)
        for name, stats in aggregate.items()
        if stats["aggregate_wer"] is not None
    ]
    selected = min(valid)[2] if valid else None
    payload = {
        "normalization": "casefold and Unicode word tokenization; punctuation excluded",
        "consultations": args.ids,
        "models": aggregate,
        "selected_default": selected,
        "selection_rule": "Lowest aggregate WER; ties go to lower total transcription time.",
        "samples": rows,
        "limitation": "Two scripted synthetic consultations; does not estimate clinical transcription quality.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"selected_default": selected, "aggregate": aggregate, "output": str(args.output)}, ensure_ascii=False, indent=2))
    return 0 if all(row["status"] == "ok" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
