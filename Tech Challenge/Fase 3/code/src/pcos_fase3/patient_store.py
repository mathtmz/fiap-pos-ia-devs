import sqlite3
from pathlib import Path

from .config import SYNTHETIC_DB


def _connection(db_path: Path = SYNTHETIC_DB) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: Path = SYNTHETIC_DB) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connection(db_path) as conn:
        conn.executescript("""
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
        """)
        count = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        if count:
            return
        patients = [(f"SYN-PCOS-{i:02d}", "18-29" if i < 7 else "30-39", "REGISTRO FICTÍCIO — NÃO É PRONTUÁRIO REAL") for i in range(1, 13)]
        conn.executemany("INSERT INTO patients VALUES (?, ?, ?)", patients)
        for patient_id, _, _ in patients:
            conn.execute("INSERT INTO exams VALUES (?, ?, ?, ?)", (patient_id, "Ultrassonografia", "simulado", "Resultado simulado disponível para discussão acadêmica."))
            status = "pendente" if int(patient_id[-2:]) % 2 else "simulado"
            conn.execute("INSERT INTO exams VALUES (?, ?, ?, ?)", (patient_id, "Avaliação metabólica", status, "Exame fictício; não usar para decisão clínica."))
            if status == "pendente":
                conn.execute("INSERT INTO pending_items VALUES (?, ?, ?)", (patient_id, "Avaliação metabólica", 1))


def patient_summary(patient_id: str | None, db_path: Path = SYNTHETIC_DB) -> dict:
    if patient_id is None:
        return {"available": False, "message": "Nenhum paciente sintético selecionado."}
    initialize_database(db_path)
    with _connection(db_path) as conn:
        patient = conn.execute("SELECT patient_id, age_band, synthetic_notice FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
        if patient is None:
            return {"available": False, "message": "Paciente sintético não encontrado."}
        exams = conn.execute("SELECT exam_name, status, summary FROM exams WHERE patient_id = ?", (patient_id,)).fetchall()
        pending = conn.execute("SELECT item FROM pending_items WHERE patient_id = ? AND simulated_alert = ?", (patient_id, 1)).fetchall()
    return {"available": True, "patient": dict(patient), "exams": [dict(row) for row in exams], "pending": [row["item"] for row in pending]}
