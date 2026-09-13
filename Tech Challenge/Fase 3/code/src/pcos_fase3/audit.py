import json
import time
import uuid
from pathlib import Path

from .config import AUDIT_FILE
from .models import AuditEvent


def new_run_id() -> str:
    return str(uuid.uuid4())


def log_event(run_id: str, node: str, status: str, decision: str, source_ids: list[str], started: float, path: Path | None = None) -> None:
    path = path or AUDIT_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    event = AuditEvent(run_id=run_id, node=node, status=status, decision=decision, source_ids=source_ids, latency_ms=int((time.perf_counter() - started) * 1000))
    with path.open("a", encoding="utf-8") as file:
        file.write(event.model_dump_json() + "\n")
