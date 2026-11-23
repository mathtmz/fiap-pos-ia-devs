"""Compare Whisper tiny with and without VAD on synthetic reference OAW04."""

from __future__ import annotations

import json
import re
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


def evaluate():
    consultation_dir = PROJECT_ROOT / "data/public/consultas"
    transcript = json.loads(
        (consultation_dir / "OAW04_transcript.json").read_text(encoding="utf-8")
    )
    reference = words(" ".join(segment["text"] for segment in transcript))
    audio_path = consultation_dir / "OAW04_consultation.wav"
    rows = []
    for use_vad in (False, True):
        started = time.perf_counter()
        result = transcribe(
            audio_path,
            model_name="tiny",
            language="pt",
            use_vad=use_vad,
        )
        edits, wer = word_error(reference, words(result["text"]))
        rows.append(
            {
                "vad": use_vad,
                "reference_words": len(reference),
                "edits": edits,
                "wer": round(wer, 4),
                "seconds": round(time.perf_counter() - started, 3),
                "segments": len(result["segments"]),
            }
        )
    payload = {
        "dataset": "OAW04 synthetic consultation",
        "model": "Whisper tiny",
        "normalization": "casefold and Unicode word tokenization; punctuation excluded",
        "comparisons": rows,
        "selected_configuration": min(rows, key=lambda row: (row["wer"], row["seconds"]))["vad"],
        "limitation": (
            "One synthetic consultation. VAD results do not validate speech detection "
            "in clinical recordings; quiet speech may be cut."
        ),
    }
    output = PROJECT_ROOT / "docs/resultados/vad_comparacao.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
