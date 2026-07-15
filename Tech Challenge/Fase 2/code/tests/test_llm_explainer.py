from pcos_fase2.llm_explainer import (
    LLMExplanationRequest,
    build_prompt,
    evaluate_response_quality,
    evaluate_response_safety,
    generate_explanation,
    gemini_llm_response,
    mock_llm_response,
    openai_llm_response,
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


def test_quality_evaluator_approves_mock_response():
    request = sample_request()
    response = mock_llm_response(request)

    quality = evaluate_response_quality(request, response)

    assert quality["numeric_consistency"]
    assert quality["covers_expected_sections"]
    assert quality["mentions_top_features"]


def test_quality_evaluator_detects_probability_mismatch():
    request = sample_request()
    inconsistent_response = mock_llm_response(request).replace("82.0%", "10.0%")

    quality = evaluate_response_quality(request, inconsistent_response)

    assert not quality["numeric_consistency"]


def test_quality_evaluator_detects_missing_sections():
    request = sample_request()
    incomplete_response = "Resposta curta sem estrutura, apenas mencionando total_foliculos."

    quality = evaluate_response_quality(request, incomplete_response)

    assert not quality["covers_expected_sections"]


def test_quality_evaluator_accepts_comma_as_decimal_separator():
    request = LLMExplanationRequest(
        model_name="Random Forest",
        probability_pcos=0.032,
        predicted_label=0,
        top_features=["total_foliculos"],
        model_metrics={"recall_pos": 0.83, "f1_pos": 0.91, "auc_roc": 0.95},
    )
    response = """Resumo: probabilidade de 3,2% para SOP.
Fatores: contagem de foliculos dentro da normalidade.
Limitacoes: dataset pequeno.
Recomendacao: avaliacao profissional."""

    quality = evaluate_response_quality(request, response)

    assert quality["numeric_consistency"]


def test_quality_evaluator_accepts_translated_feature_names():
    request = LLMExplanationRequest(
        model_name="Random Forest",
        probability_pcos=0.032,
        predicted_label=0,
        top_features=["Follicle No. (R)", "total_foliculos", "hair growth(Y/N)"],
        model_metrics={"recall_pos": 0.83, "f1_pos": 0.91, "auc_roc": 0.95},
    )
    response = """Resumo: risco baixo de SOP.
Fatores: a contagem de foliculos e a ausencia de crescimento de pelo reduziram o risco estimado.
Limitacoes: dataset pequeno.
Recomendacao: avaliacao profissional."""

    quality = evaluate_response_quality(request, response)

    assert quality["mentions_top_features"]


def test_quality_evaluator_rejects_unrelated_features():
    request = LLMExplanationRequest(
        model_name="Random Forest",
        probability_pcos=0.032,
        predicted_label=0,
        top_features=["AMH(ng/mL)"],
        model_metrics={"recall_pos": 0.83, "f1_pos": 0.91, "auc_roc": 0.95},
    )
    response = """Resumo: risco baixo de SOP, sem relacao com nenhum fator relevante.
Fatores: nenhum em especifico.
Limitacoes: dataset pequeno.
Recomendacao: avaliacao profissional."""

    quality = evaluate_response_quality(request, response)

    assert not quality["mentions_top_features"]


def test_openai_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    try:
        openai_llm_response(sample_request())
    except ValueError as error:
        assert "LLM_API_KEY" in str(error)
    else:
        raise AssertionError("Provider OpenAI deveria exigir chave de API.")


def test_gemini_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    try:
        gemini_llm_response(sample_request())
    except ValueError as error:
        assert "GEMINI_API_KEY" in str(error)
    else:
        raise AssertionError("Provider Gemini deveria exigir chave de API.")
