from pathlib import Path

from pcos_fase3.graph import run_triage


def test_grounded_workflow(tmp_path, monkeypatch):
    import pcos_fase3.audit as audit
    monkeypatch.setattr(audit, "AUDIT_FILE", tmp_path / "audit.jsonl")
    result = run_triage({"patient_id": "SYN-PCOS-01", "question": "Quais são os limites da triagem?"})
    assert result["status"] == "ok"
    assert result["sources"]
    assert "sanitized_audit" in result["trace"]


def test_abstains_when_no_sources():
    result = run_triage({"patient_id": None, "question": "xilofone quântico interplanetário"})
    assert result["status"] == "abstained"


def test_invalid_synthetic_patient_id_is_rejected_at_boundary():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        run_triage({"patient_id": "1 OR 1=1", "question": "Quais são os limites?"})


def test_audit_does_not_store_question_or_patient_text(tmp_path, monkeypatch):
    import pcos_fase3.audit as audit
    audit_file = tmp_path / "audit.jsonl"
    monkeypatch.setattr(audit, "AUDIT_FILE", audit_file)
    question = "Quais são os limites da triagem?"
    run_triage({"patient_id": "SYN-PCOS-01", "question": question})
    logged = audit_file.read_text(encoding="utf-8")
    assert question not in logged
    assert "SYN-PCOS-01" not in logged
