"""Avalia casos sintéticos por ocorrência explícita, pergunta e negação."""

import json, sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE / "src"))
from fisio_fase4.audio_text import analyze_segments

cases = [
    ("Sinto dor no ombro.", True),
    ("Não sinto dor.", False),
    ("Você sente dor?", False),
    ("Estou com falta de ar.", True),
    ("Estou descansado.", False),
    ("Nega dor.", False),
]
rows = []
for text, expected in cases:
    out = analyze_segments([{"start": 0, "end": 2, "text": text}], "sintetico")
    rows.append(
        {
            "text": text,
            "expected_alert": expected,
            "actual_alert": bool(out["events"]),
            "review_items": len(out["review_items"]),
            "terms": out["chunks"][0]["analysis"]["terms"],
        }
    )
    print(rows[-1], flush=True)
tp = sum(r["actual_alert"] and r["expected_alert"] for r in rows)
fp = sum(r["actual_alert"] and not r["expected_alert"] for r in rows)
fn = sum(not r["actual_alert"] and r["expected_alert"] for r in rows)
p = tp / (tp + fp) if tp + fp else 0
rec = tp / (tp + fn) if tp + fn else 0
result = {
    "cases": rows,
    "tp": tp,
    "fp": fp,
    "fn": fn,
    "precision": p,
    "recall": rec,
    "f1": 2 * p * rec / (p + rec) if p + rec else 0,
    "limitation": "Seis frases sintéticas curtas, rótulos manuais; não avalia consultas reais.",
}
path = CODE / "outputs/avaliacao/texto_contexto.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False))
