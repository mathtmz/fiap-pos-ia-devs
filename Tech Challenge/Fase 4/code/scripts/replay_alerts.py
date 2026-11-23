"""Reproduz eventos e emite alertas locais ao ritmo configurado."""

import argparse, json, time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("report", type=Path)
p.add_argument("--speed", type=float, default=1.0)
args = p.parse_args()
if args.speed <= 0:
    p.error("--speed deve ser positivo")
data = json.loads(args.report.read_text())
events = sorted(data["events"], key=lambda e: e["time_s"])
start = time.monotonic()
for item in events:
    deadline = start + float(item["time_s"]) / args.speed
    time.sleep(max(0, deadline - time.monotonic()))
    print(
        json.dumps(
            {"elapsed_s": round(time.monotonic() - start, 3), "event": item},
            ensure_ascii=False,
        ),
        flush=True,
    )
