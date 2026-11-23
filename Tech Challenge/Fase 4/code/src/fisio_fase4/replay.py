"""Timed local playback for precomputed, timestamped case events."""

from __future__ import annotations

import json
import math
import statistics
import time
from pathlib import Path


def replay_events(events, speed=1.0, output_path=None, on_event=None):
    if speed <= 0:
        raise ValueError("Playback speed must be positive.")
    ordered = sorted(
        events,
        key=lambda item: (float(item["time_s"]), item.get("event_id", "")),
    )
    output_file = Path(output_path) if output_path else None
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
    latencies, records, seen = [], [], set()
    started = time.monotonic()
    handle = output_file.open("w", encoding="utf-8") if output_file else None
    try:
        for event in ordered:
            event_id = event.get("event_id")
            if event_id and event_id in seen:
                raise ValueError(f"Duplicate event id during playback: {event_id}")
            if event_id:
                seen.add(event_id)
            deadline = started + float(event["time_s"]) / speed
            time.sleep(max(0.0, deadline - time.monotonic()))
            observed = time.monotonic()
            latency = max(0.0, observed - deadline)
            latencies.append(latency)
            record = {
                "scheduled_time_s": float(event["time_s"]),
                "elapsed_time_s": round(observed - started, 4),
                "delivery_latency_ms": round(latency * 1000, 3),
                "event": event,
            }
            records.append(record)
            if handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                handle.flush()
            if on_event:
                on_event(record)
    finally:
        if handle:
            handle.close()
    p95 = (
        sorted(latencies)[max(0, math.ceil(0.95 * len(latencies)) - 1)]
        if latencies
        else 0.0
    )
    return {
        "speed": speed,
        "events_expected": len(ordered),
        "events_delivered": len(records),
        "duplicate_ids": 0,
        "median_delivery_latency_ms": round(statistics.median(latencies) * 1000, 3)
        if latencies
        else 0.0,
        "p95_delivery_latency_ms": round(p95 * 1000, 3),
        "log": str(output_file) if output_file else None,
        "limitation": "Eventos multimodais foram calculados antes da reprodução; esta medição cobre a entrega local temporizada.",
    }, records
