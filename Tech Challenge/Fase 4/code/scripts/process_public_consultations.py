"""Process authorized local copies of the two referenced public videos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
sys.path.insert(0, str(CODE_DIR / "src"))
sys.path.insert(0, str(CODE_DIR / "scripts"))

from fisio_fase4.pipeline import run_case
from summarize_public_consultations import CONSULTATIONS, summarize


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--therapy-audio",
        type=Path,
        required=True,
        help="Authorized local audio for the manual-therapy source.",
    )
    parser.add_argument(
        "--hip-audio",
        type=Path,
        required=True,
        help="Authorized local audio for the hip-rehabilitation source.",
    )
    parser.add_argument(
        "--no-qwen",
        action="store_true",
        help="Run Whisper only; Qwen analysis is enabled by default.",
    )
    args = parser.parse_args()

    supplied = {
        "terapia_manual": args.therapy_audio,
        "reabilitacao_quadril": args.hip_audio,
    }
    for item in CONSULTATIONS:
        source = supplied[item["id"]].expanduser().resolve()
        if not source.is_file():
            parser.error(f"Audio file not found: {source}")
        output_dir = CODE_DIR / "outputs" / (
            "consulta_real_terapia_completa"
            if item["id"] == "terapia_manual"
            else "consulta_real_quadril_completa"
        )
        result = run_case(
            case_id=item["id"],
            output_dir=output_dir,
            audio=source,
            qwen=not args.no_qwen,
            whisper_model="small",
        )
        audio = result["modalities"]["audio"]
        if audio["status"] != "ok":
            raise RuntimeError(f"{item['id']} failed: {audio.get('error')}")
        text = audio["result"]["transcription"].get("text", "")
        print(
            json.dumps(
                {
                    "id": item["id"],
                    "status": audio["status"],
                    "word_count": len(text.split()),
                    "processing_elapsed_s": audio["elapsed_s"],
                    "report": str(output_dir / "relatorio.json"),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    payload = {
        "description": (
            "Minimized processing metadata for two public Portuguese videos. "
            "The original media remains at the linked sources and no transcript is included."
        ),
        "consultations": [summarize(item) for item in CONSULTATIONS],
    }
    summary_path = PROJECT_ROOT / "docs/resultados/consultas_publicas_resumo.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Minimized summary written to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
