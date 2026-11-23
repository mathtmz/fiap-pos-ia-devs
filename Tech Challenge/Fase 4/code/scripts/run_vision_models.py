"""Executa os dois modelos sobre um quadro e salva resultados rastreáveis."""

import argparse, sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
sys.path.insert(0, str(CODE / "src"))
from fisio_fase4.vision_models import analyze_frame
from fisio_fase4.analysis import write_json

parser = argparse.ArgumentParser()
parser.add_argument("video")
parser.add_argument("--time", type=float, default=1.0)
parser.add_argument("--output", default=str(CODE / "outputs/visao_modelos"))
args = parser.parse_args()
r = analyze_frame(
    args.video, args.output, ROOT / "data/public/modelos/openpose", args.time
)
write_json(Path(args.output) / "resultado.json", r)
print({k: v.get("status") for k, v in r.items() if isinstance(v, dict)})
