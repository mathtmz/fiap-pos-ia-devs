import argparse
import json
from pathlib import Path
import sys

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
sys.path.insert(0, str(CODE / "src"))
from fisio_fase4.pipeline import run_case

p = argparse.ArgumentParser(description="Executa caso multimodal acadêmico.")
p.add_argument("--video")
p.add_argument("--audio")
p.add_argument("--normal", action="store_true")
p.add_argument("--no-qwen", action="store_true")
p.add_argument("--diarize", action="store_true", help="Enable experimental speaker grouping.")
p.add_argument(
    "--speaker-1-role",
    choices=["não identificado", "paciente", "profissional"],
    default="não identificado",
)
p.add_argument(
    "--speaker-2-role",
    choices=["não identificado", "paciente", "profissional"],
    default="não identificado",
)
p.add_argument("--vision-fps", type=float, default=5.0)
p.add_argument("--output", default=str(CODE / "outputs/demo"))
p.add_argument("--case-id", default="caso_demo")
a = p.parse_args()
suffix = "normal" if a.normal else "anomalia"
r = run_case(
    a.case_id,
    a.output,
    vitals=ROOT / f"data/synthetic/vitais_{suffix}.csv",
    prescriptions=ROOT / f"data/synthetic/prescricoes_{suffix}.csv",
    video=a.video,
    audio=a.audio,
    qwen=not a.no_qwen,
    diarize=a.diarize,
    speaker_roles={
        "locutor_1": a.speaker_1_role,
        "locutor_2": a.speaker_2_role,
    },
    vision_fps=a.vision_fps,
)
print(
    json.dumps(
        {
            "modalities": {k: v["status"] for k, v in r["modalities"].items()},
            "events": len(r["events"]),
            "alerts": len(r["alerts"]),
            "seconds": r["processing_elapsed_s"],
        },
        ensure_ascii=False,
        indent=2,
    )
)
