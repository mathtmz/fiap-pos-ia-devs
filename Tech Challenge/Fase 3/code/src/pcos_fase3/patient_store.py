import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import CASE_PROFILES_FILE, SYNTHETIC_DB

DEMO_NOTICE = "REGISTRO DE DEMONSTRAÇÃO ACADÊMICA — NÃO É PRONTUÁRIO REAL"


def _connection(db_path: Path = SYNTHETIC_DB) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def _managed_connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Commit or roll back work and always release the SQLite file handle."""
    connection = _connection(db_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _load_profiles() -> list[dict]:
    if not CASE_PROFILES_FILE.is_file():
        return []
    return [
        json.loads(line)
        for line in CASE_PROFILES_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def initialize_database(db_path: Path = SYNTHETIC_DB) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    profiles = _load_profiles()
    with _managed_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY CHECK(patient_id GLOB 'SYN-PCOS-[0-9][0-9]'),
                age_band TEXT NOT NULL,
                synthetic_notice TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS exams (
                patient_id TEXT NOT NULL, exam_name TEXT NOT NULL, status TEXT NOT NULL,
                summary TEXT NOT NULL, FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
            );
            CREATE TABLE IF NOT EXISTS pending_items (
                patient_id TEXT NOT NULL, item TEXT NOT NULL, simulated_alert INTEGER NOT NULL,
                FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
            );
            CREATE TABLE IF NOT EXISTS reported_facts (
                patient_id TEXT NOT NULL, fact_order INTEGER NOT NULL,
                category TEXT NOT NULL, detail TEXT NOT NULL,
                PRIMARY KEY(patient_id, fact_order),
                FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
            );
            """
        )

        conn.execute("UPDATE patients SET synthetic_notice = ?", (DEMO_NOTICE,))
        conn.execute(
            "UPDATE exams SET summary = ?",
            ("Registro demonstrativo disponível para revisão profissional.",),
        )
        conn.execute("UPDATE exams SET status = ? WHERE lower(status) = ?", ("Concluído", "simulado"))

        for profile in profiles:
            patient_id = profile["patient_id"]
            inserted = conn.execute(
                "INSERT OR IGNORE INTO patients VALUES (?, ?, ?)",
                (patient_id, profile["age_band"], DEMO_NOTICE),
            ).rowcount
            conn.execute(
                "UPDATE patients SET age_band = ?, synthetic_notice = ? WHERE patient_id = ?",
                (profile["age_band"], DEMO_NOTICE, patient_id),
            )
            for order, fact in enumerate(profile.get("reported_facts", [])):
                conn.execute(
                    """INSERT INTO reported_facts VALUES (?, ?, ?, ?)
                       ON CONFLICT(patient_id, fact_order) DO UPDATE SET
                       category = excluded.category, detail = excluded.detail""",
                    (patient_id, order, fact["category"], fact["detail"]),
                )
            if inserted:
                conn.execute(
                    "INSERT INTO exams VALUES (?, ?, ?, ?)",
                    (patient_id, "Ultrassonografia", "Concluído", "Registro demonstrativo disponível para revisão profissional."),
                )
                status = "Pendente" if int(patient_id[-2:]) % 2 else "Concluído"
                conn.execute(
                    "INSERT INTO exams VALUES (?, ?, ?, ?)",
                    (patient_id, "Avaliação metabólica", status, "Registro demonstrativo disponível para revisão profissional."),
                )
                if status == "Pendente":
                    conn.execute(
                        "INSERT INTO pending_items VALUES (?, ?, ?)",
                        (patient_id, "Avaliação metabólica", 1),
                    )


def patient_summary(patient_id: str | None, db_path: Path = SYNTHETIC_DB) -> dict:
    if patient_id is None:
        return {"available": False, "message": "Nenhum registro selecionado."}
    initialize_database(db_path)
    with _managed_connection(db_path) as conn:
        patient = conn.execute(
            "SELECT patient_id, age_band, synthetic_notice FROM patients WHERE patient_id = ?",
            (patient_id,),
        ).fetchone()
        if patient is None:
            return {"available": False, "message": "Registro não encontrado."}
        exams = conn.execute(
            "SELECT exam_name, status, summary FROM exams WHERE patient_id = ?",
            (patient_id,),
        ).fetchall()
        pending = conn.execute(
            "SELECT item FROM pending_items WHERE patient_id = ? AND simulated_alert = ?",
            (patient_id, 1),
        ).fetchall()
        reported_facts = conn.execute(
            "SELECT category, detail FROM reported_facts WHERE patient_id = ? ORDER BY fact_order",
            (patient_id,),
        ).fetchall()
    return {
        "available": True,
        "patient": dict(patient),
        "reported_facts": [dict(row) for row in reported_facts],
        "exams": [dict(row) for row in exams],
        "pending": [row["item"] for row in pending],
    }
