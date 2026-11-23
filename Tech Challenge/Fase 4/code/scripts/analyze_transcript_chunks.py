"""Analisa todos os segmentos de uma transcrição existente em blocos de até 3000 caracteres."""

import argparse, json, sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE / "src"))
from fisio_fase4.audio_text import analyze_text, text_events

p = argparse.ArgumentParser()
p.add_argument("report", type=Path)
p.add_argument("--case-id", default="consulta_terapia")
a = p.parse_args()
data = json.loads(a.report.read_text())
segments = data["modalities"]["audio"]["result"]["transcription"]["segments"]
groups = []
group = []
length = 0
for seg in segments:
    if group and length + len(seg["text"]) > 3000:
        groups.append(group)
        group = []
        length = 0
    group.append(seg)
    length += len(seg["text"])
if group:
    groups.append(group)
results = []
for chunk in groups:
    analysis = analyze_text(" ".join(s["text"] for s in chunk))
    results.append(
        {
            "inicio_s": chunk[0]["start"],
            "fim_s": chunk[-1]["end"],
            "sentimento": analysis["sentiment"],
            "termos": analysis["terms"],
            "eventos": text_events(analysis, chunk, a.case_id),
            "status": analysis["status"],
        }
    )
out = a.report.parent / "analise_por_trechos.json"
out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
print("Resultado:", out)
