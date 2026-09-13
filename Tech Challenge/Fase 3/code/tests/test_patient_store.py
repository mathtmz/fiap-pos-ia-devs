from pcos_fase3.patient_store import initialize_database, patient_summary


def test_synthetic_patient_and_pending_exam(tmp_path):
    db = tmp_path / "synthetic.sqlite"
    initialize_database(db)
    result = patient_summary("SYN-PCOS-01", db)
    assert result["available"] is True
    assert result["pending"] == ["Avaliação metabólica"]
    assert "FICTÍCIO" in result["patient"]["synthetic_notice"]


def test_nonexistent_patient_is_not_disclosed(tmp_path):
    db = tmp_path / "synthetic.sqlite"
    initialize_database(db)
    assert patient_summary("SYN-PCOS-99", db)["available"] is False
