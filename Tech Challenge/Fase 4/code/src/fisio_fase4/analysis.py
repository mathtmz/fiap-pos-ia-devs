"""Regras experimentais rastreáveis; não são limites clínicos validados."""

from __future__ import annotations
import json
import hashlib
import math
from pathlib import Path

# Limiares didáticos, escolhidos para o caso sintético, sem propósito clínico.
LIMITS = {
    "heart_rate": (50, 120),
    "systolic_bp": (90, 160),
    "diastolic_bp": (50, 100),
    "spo2": (92, 100),
}
UNITS = {
    "heart_rate": "bpm",
    "systolic_bp": "mmHg",
    "diastolic_bp": "mmHg",
    "spo2": "%",
}


def refresh_event_id(payload):
    identity = {
        key: payload.get(key)
        for key in (
            "case_id",
            "time_s",
            "modality",
            "kind",
            "evidence",
            "rule",
            "source",
            "model",
            "frame_index",
        )
    }
    payload["event_id"] = hashlib.sha256(
        json.dumps(identity, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    return payload


def event(
    case_id,
    time_s,
    modality,
    kind,
    evidence,
    rule,
    *,
    source=None,
    model=None,
    frame_index=None,
    confidence=None,
    review_status="revisao_humana_requerida",
):
    payload = {
        "case_id": case_id,
        "time_s": round(float(time_s), 3),
        "modality": modality,
        "kind": kind,
        "evidence": evidence,
        "rule": rule,
        "source": source,
        "model": model,
        "frame_index": frame_index,
        "confidence": confidence,
        "review_status": review_status,
    }
    return refresh_event_id(payload)


def detect_vitals(rows, case_id):
    findings = []
    for row in rows:
        for name, (low, high) in LIMITS.items():
            value = row.get(name)
            if value in (None, ""):
                continue
            value = float(value)
            if not math.isfinite(value):
                continue
            if value < low or value > high:
                findings.append(
                    event(
                        case_id,
                        row["time_s"],
                        "sinais_vitais",
                        name,
                        f"{name}: {value:g} {UNITS[name]}",
                        f"Fora do intervalo experimental [{low}, {high}]",
                    )
                )
    return findings


def detect_prescriptions(rows, case_id):
    findings, previous = [], {}
    for row in sorted(rows, key=lambda r: float(r["time_s"])):
        name = str(row["medication"]).strip().casefold()
        dose = float(row["dose"])
        unit = str(row["unit"]).strip().casefold()
        if not name or not unit or not math.isfinite(dose) or dose <= 0:
            raise ValueError("Prescrição requer medicamento, unidade e dose positiva.")
        prior = previous.get(name)
        if prior and prior[1] != unit:
            findings.append(
                event(
                    case_id,
                    row["time_s"],
                    "prescricao",
                    "unidade_alterada",
                    f"{name}: {prior[0]:g} {prior[1]} → {dose:g} {unit}",
                    "Unidades divergentes exigem revisão; sem comparação numérica",
                )
            )
        elif prior and abs(dose - prior[0]) / prior[0] >= 0.5:
            findings.append(
                event(
                    case_id,
                    row["time_s"],
                    "prescricao",
                    "variacao_dose",
                    f"{name}: {prior[0]:g} → {dose:g} {unit}",
                    "Variação relativa de dose >= 50% entre registros consecutivos",
                )
            )
        previous[name] = (dose, unit)
    return findings


def fuse_events(events, window_s=30):
    if window_s <= 0:
        raise ValueError("A janela deve ser positiva.")
    grouped = {}
    for item in events:
        key = (item["case_id"], int(float(item["time_s"]) // window_s))
        grouped.setdefault(key, []).append(item)
    return [
        {
            "case_id": case,
            "window_start_s": bucket * window_s,
            "window_end_s": (bucket + 1) * window_s,
            "modalities": sorted({x["modality"] for x in items}),
            "events": sorted(items, key=lambda x: x["time_s"]),
            "message": "Revisão humana necessária; critérios experimentais.",
        }
        for (case, bucket), items in sorted(grouped.items())
    ]


def write_json(path, payload):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
