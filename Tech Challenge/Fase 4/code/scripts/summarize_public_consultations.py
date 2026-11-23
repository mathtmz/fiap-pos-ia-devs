"""Create a minimized, transcript-free summary from local consultation reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
OUTPUT_PATH = PROJECT_ROOT / "docs/resultados/consultas_publicas_resumo.json"

CONSULTATIONS = (
    {
        "id": "terapia_manual",
        "title": "A terapia manual na prática! (ao vivo)",
        "url": "https://www.youtube.com/watch?v=Y3Au3GcBbbg",
        "report": CODE_DIR / "outputs/consulta_real_terapia_completa/relatorio.json",
        "legacy_model": "tiny",
    },
    {
        "id": "reabilitacao_quadril",
        "title": "Artroplastia de quadril: fisioterapia e recuperação no pós-operatório",
        "url": "https://www.youtube.com/watch?v=ihY3hJ9-RBg",
        "report": CODE_DIR / "outputs/consulta_real_quadril_completa/relatorio.json",
        "legacy_model": "tiny",
    },
)


def summarize(item: dict) -> dict:
    report_path = Path(item["report"])
    if not report_path.is_file():
        raise FileNotFoundError(
            f"Missing local analysis {report_path}. Process the source media first."
        )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    audio = report.get("modalities", {}).get("audio", {})
    result = audio.get("result", {})
    transcription = result.get("transcription", {})
    acoustics = result.get("acoustics", {})
    configuration = result.get("configuration", {})
    return {
        "id": item["id"],
        "title": item["title"],
        "source_url": item["url"],
        "source_media_stored_in_git": False,
        "authorization": "Informada pela equipe; autorização não é armazenada neste repositório.",
        "processing_status": audio.get("status", "ausente"),
        "whisper_model": configuration.get("whisper_model", item.get("legacy_model")),
        "language_detected": transcription.get("language"),
        "media_duration_s": acoustics.get("duration_s"),
        "transcribed_word_count": len(transcription.get("text", "").split()),
        "segment_count": len(transcription.get("segments", [])),
        "processing_elapsed_s": audio.get("elapsed_s"),
        "manual_reference_available": False,
        "wer": None,
        "transcript_included": False,
        "interpretation": (
            "Descriptive processing summary only. No transcript or clinical "
            "interpretation is retained in this artifact."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    payload = {
        "description": (
            "Minimized processing metadata for two public Portuguese videos. "
            "The original media remains at the linked sources and no transcript is included."
        ),
        "consultations": [summarize(item) for item in CONSULTATIONS],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Minimized summary written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
