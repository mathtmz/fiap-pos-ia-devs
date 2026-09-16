from scripts.run_evaluation import evaluate_retrieval


def test_retrieval_metrics_cover_relevant_sources():
    cases = [
        {"id": "one", "question": "Limites do assistente", "relevant_source_ids": ["FAQ"]},
        {"id": "two", "question": "Exames pendentes", "relevant_source_ids": ["PENDING"]},
    ]

    def fake_retrieve(question, k):
        source_id = "FAQ" if "Limites" in question else "PENDING"
        return [{"source_id": source_id}]

    import scripts.run_evaluation as evaluation

    original = evaluation.retrieve
    evaluation.retrieve = fake_retrieve
    try:
        metrics, per_case = evaluate_retrieval(cases, k=3)
    finally:
        evaluation.retrieve = original
    assert metrics["case_count"] == 2
    assert metrics["precision_at_3"] == 1 / 3
    assert metrics["recall_at_3"] == 1.0
    assert metrics["mrr"] == 1.0
    assert len(per_case) == 2
