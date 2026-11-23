"""Calcula WER da consulta OAW04 a partir da execução existente."""

import json, re
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
ref = json.loads((ROOT / "data/public/consultas/OAW04_transcript.json").read_text())
result = json.loads((CODE / "outputs/consulta_oaw04/relatorio.json").read_text())
words = lambda text: re.findall(r"\w+", text.casefold(), flags=re.UNICODE)
a = words(" ".join(turn["text"] for turn in ref))
b = words(result["modalities"]["audio"]["result"]["transcription"]["text"])
previous = list(range(len(b) + 1))
for i, x in enumerate(a, 1):
    row = [i]
    for j, y in enumerate(b, 1):
        row.append(min(row[-1] + 1, previous[j] + 1, previous[j - 1] + (x != y)))
    previous = row
print(
    json.dumps(
        {
            "reference_words": len(a),
            "edit_distance": previous[-1],
            "wer": round(previous[-1] / len(a), 4),
            "normalization": "casefold e remoção de pontuação",
        },
        ensure_ascii=False,
        indent=2,
    )
)
