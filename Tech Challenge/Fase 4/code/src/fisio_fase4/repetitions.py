"""Segmentação exploratória de abdução; não identifica outras atividades."""

from statistics import median


def summarize_repetitions(
    angles, measurements, side="direito", low=35, high=55, min_samples=3
):
    samples = sorted(
        (a for a in angles if a["side"] == side), key=lambda a: a["time_s"]
    )
    repetitions = []
    active = []
    armed = False

    def finish(reason):
        if not active:
            return
        start, end = active[0]["time_s"], active[-1]["time_s"]
        values = [
            m for m in measurements if m["side"] == side and start <= m["time_s"] <= end
        ]
        repetitions.append(
            {
                "start_s": start,
                "end_s": end,
                "side": side,
                "samples": len(active),
                "max_angle": round(max(x["angle"] for x in active), 1),
                "min_elbow_angle": (
                    round(min(x["elbow_angle"] for x in values), 1) if values else None
                ),
                "max_trunk_tilt": (
                    round(max(x["trunk_tilt"] for x in values), 1) if values else None
                ),
                "status": (
                    "avaliavel"
                    if len(active) >= min_samples and values and reason == "completa"
                    else "inconclusivo"
                ),
                "reason": reason,
                "events": [],
            }
        )

    for i, item in enumerate(samples):
        smooth = median(x["angle"] for x in samples[max(0, i - 1) : i + 2])
        if active and item["time_s"] - active[-1]["time_s"] > 1.0:
            finish("perda de pose")
            active = []
            armed = False
        if not active:
            if smooth < low:
                armed = True
            if armed and smooth >= low:
                active = [item]
        else:
            active.append(item)
            if smooth < low:
                finish("completa")
                active = []
                armed = True
    if active:
        finish("trecho incompleto")
    return repetitions


def evaluate_repetitions(repetitions, thresholds, case_id):
    from .analysis import event

    checks = [
        ("max_angle", "amplitude_baixa", "lt"),
        ("min_elbow_angle", "cotovelo_flexionado", "lt"),
        ("max_trunk_tilt", "tronco_inclinado", "gt"),
    ]
    for rep in repetitions:
        if rep["status"] != "avaliavel":
            continue
        for field, kind, op in checks:
            if field not in thresholds or rep[field] is None:
                continue
            threshold = thresholds[field]
            value = rep[field]
            if value < threshold if op == "lt" else value > threshold:
                rep["events"].append(
                    event(
                        case_id,
                        rep["start_s"],
                        "video",
                        kind,
                        f'{field}: {value}° na repetição {rep["start_s"]}–{rep["end_s"]} s',
                        f"limiar experimental {op} {threshold}°",
                    )
                )
    return repetitions
