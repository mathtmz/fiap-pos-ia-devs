from pcos_fase3.patient_store import initialize_database, patient_summary


def test_synthetic_patient_and_pending_exam(workspace_file):
    db = workspace_file
    initialize_database(db)
    result = patient_summary("SYN-PCOS-01", db)
    assert result["available"] is True
    assert result["pending"] == ["Avaliação metabólica"]
    assert "DEMONSTRAÇÃO" in result["patient"]["synthetic_notice"]
    assert len(result["reported_facts"]) == 3
    assert result["reported_facts"][0]["category"] == "Queixa relatada"


def test_all_demo_records_have_facts_and_exams(workspace_file):
    initialize_database(workspace_file)
    for index in range(1, 13):
        result = patient_summary(f"SYN-PCOS-{index:02d}", workspace_file)
        assert result["available"] is True
        assert result["reported_facts"]
        assert result["exams"]


def test_nonexistent_patient_is_not_disclosed(workspace_file):
    db = workspace_file
    initialize_database(db)
    assert patient_summary("SYN-PCOS-99", db)["available"] is False
