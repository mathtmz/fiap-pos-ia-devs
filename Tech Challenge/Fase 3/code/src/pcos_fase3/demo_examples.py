"""Load deliberately isolated, static examples for the demonstration UI."""
import json

from .config import DEMO_DIAGNOSIS_FILE


def load_demo_diagnosis_example() -> dict:
    example = json.loads(DEMO_DIAGNOSIS_FILE.read_text(encoding="utf-8"))
    if not all(example.get(flag) is True for flag in ("fictional", "demo_only", "not_for_triage")):
        raise ValueError("O exemplo de diagnóstico precisa permanecer isolado e marcado como demonstração.")
    return example
