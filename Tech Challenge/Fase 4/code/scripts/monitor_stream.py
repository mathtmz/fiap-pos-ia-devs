"""Monitora incrementos de CSV simulando a chegada temporal de dados."""

import argparse, csv, json, sys, time
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
sys.path.insert(0, str(CODE / "src"))
from fisio_fase4.analysis import detect_vitals, detect_prescriptions


def read(path, kind):
    with open(path, encoding="utf8", newline="") as f:
        return [(float(row["time_s"]), kind, row) for row in csv.DictReader(f)]


def monitor(vitals, prescriptions, speed=1, case_id="caso_demo"):
    if speed <= 0:
        raise ValueError("A velocidade deve ser positiva.")
    timeline = sorted(
        read(vitals, "vital") + read(prescriptions, "prescricao"),
        key=lambda x: (x[0], x[1]),
    )
    start = time.monotonic()
    history = []
    for stamp, kind, row in timeline:
        time.sleep(max(0, start + stamp / speed - time.monotonic()))
        arrival = time.monotonic()
        if kind == "vital":
            events = detect_vitals([row], case_id)
        else:
            before = len(detect_prescriptions(history, case_id))
            history.append(row)
            events = detect_prescriptions(history, case_id)[before:]
        yield {
            "source_time_s": stamp,
            "type": kind,
            "elapsed_s": round(time.monotonic() - start, 4),
            "processing_latency_ms": round((time.monotonic() - arrival) * 1000, 3),
            "events": events,
        }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--speed", type=float, default=1.0)
    p.add_argument("--normal", action="store_true")
    p.add_argument("--output", type=Path, default=CODE / "outputs/stream/eventos.jsonl")
    a = p.parse_args()
    suffix = "normal" if a.normal else "anomalia"
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("w", encoding="utf8") as f:
        for item in monitor(
            ROOT / f"data/synthetic/vitais_{suffix}.csv",
            ROOT / f"data/synthetic/prescricoes_{suffix}.csv",
            a.speed,
        ):
            line = json.dumps(item, ensure_ascii=False)
            print(line, flush=True)
            f.write(line + "\n")
            f.flush()
