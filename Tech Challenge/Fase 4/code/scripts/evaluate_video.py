"""Avaliação exploratória em duas repetições: não representa validação clínica."""

from pathlib import Path
import sys, json, time

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
sys.path.insert(0, str(CODE / "src"))
from fisio_fase4.video import analyze_video

rows = []
for label in ["correto", "incorreto"]:
    t = time.perf_counter()
    result = analyze_video(
        ROOT / f"data/public/rehab_{label}.mp4",
        CODE / f"outputs/avaliacao/{label}.mp4",
        "video_avaliacao",
    )
    predicted = bool(result["events"])
    expected = label == "incorreto"
    rows.append(
        {
            "segmento": label,
            "rotulo_desvio": expected,
            "predicao_desvio": predicted,
            "acerto": predicted == expected,
            "segundos": round(time.perf_counter() - t, 2),
            "frames": result["frames"],
            "frames_com_pose": result["frames_pose"],
            "quadros_analisados": result["frames_analyzed"],
            "angulo_maximo": max((v["angle"] for v in result["angles"]), default=None),
        }
    )
print(json.dumps(rows, ensure_ascii=False, indent=2))
(CODE / "outputs/avaliacao/metricas.json").write_text(
    json.dumps(rows, ensure_ascii=False, indent=2)
)
