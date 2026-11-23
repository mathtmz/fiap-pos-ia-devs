"""Compara alertas por trecho com rótulos PM_101; não é validação clínica."""

import json, sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
sys.path.insert(0, str(CODE / "src"))
from fisio_fase4.video import analyze_video

rows = []
for index, name in enumerate(
    ["normal", "erro_1", "erro_2", "erro_3", "erro_4", "erro_5"]
):
    result = analyze_video(
        ROOT / f"data/public/pm101_{name}.mp4",
        CODE / f"outputs/avaliacao_repeticoes/{name}.mp4",
        name,
        thresholds={"max_angle": 132.35},
    )
    rows.append(
        {
            "segmento": name,
            "rotulo_incorreto": index > 0,
            "alerta": bool(result["events"]),
            "repeticoes": len(result["repetition_details"]),
            "eventos": len(result["events"]),
        }
    )
out = CODE / "outputs/avaliacao_repeticoes/resultados.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(rows, ensure_ascii=False, indent=2))
print(json.dumps(rows, ensure_ascii=False, indent=2))
