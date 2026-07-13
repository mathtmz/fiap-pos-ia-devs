from pcos_fase2.llm_explainer import (
    LLMExplanationRequest,
    build_prompt,
    evaluate_response_safety,
    generate_explanation,
)


def sample_request() -> LLMExplanationRequest:
    return LLMExplanationRequest(
        model_name="Random Forest",
        probability_pcos=0.82,
        predicted_label=1,
        top_features=["total_foliculos", "soma_sintomas", "AMH(ng/mL)"],
        model_metrics={"recall_pos": 0.90, "f1_pos": 0.88, "auc_roc": 0.96},
    )


def test_prompt_contains_context_and_safety_rules():
    prompt = build_prompt(sample_request())

    assert "Sindrome dos Ovarios Policisticos" in prompt
    assert "Nao forneca diagnostico definitivo" in prompt
    assert "total_foliculos" in prompt
    assert "82.0%" in prompt


def test_mock_explanation_is_safe_enough_for_demo(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    response, safety = generate_explanation(sample_request())

    assert "triagem" in response.lower()
    assert safety["mentions_triage_support"]
    assert safety["mentions_professional"]
    assert safety["avoids_forbidden_terms"]


def test_safety_evaluator_rejects_prescriptive_text():
    safety = evaluate_response_safety("Este e um diagnostico definitivo. Inicie tratamento.")

    assert not safety["avoids_forbidden_terms"]
