from __future__ import annotations

import os
from dataclasses import dataclass


SYSTEM_RULES = """Voce e um assistente de apoio a interpretacao de modelos de machine learning em saude.
Nao forneca diagnostico definitivo, prescricao ou conduta medica.
Explique os resultados como apoio a triagem clinica e recomende avaliacao profissional quando adequado."""


@dataclass(frozen=True)
class LLMExplanationRequest:
    model_name: str
    probability_pcos: float
    predicted_label: int
    top_features: list[str]
    model_metrics: dict[str, float]


def build_prompt(request: LLMExplanationRequest) -> str:
    predicted_text = "maior risco estimado de SOP" if request.predicted_label == 1 else "menor risco estimado de SOP"
    return f"""{SYSTEM_RULES}

Contexto:
- Doenca-alvo: Sindrome dos Ovarios Policisticos (SOP).
- Modelo: {request.model_name}.
- Classe positiva: paciente com SOP.
- Probabilidade prevista para SOP: {request.probability_pcos:.1%}.
- Resultado previsto: {predicted_text}.
- Principais fatores globais do modelo: {", ".join(request.top_features)}.
- Metricas globais do modelo: {request.model_metrics}.

Tarefa:
1. Explique em linguagem natural por que o modelo sugeriu esse resultado.
2. Destaque fatores que merecem atencao clinica, sem inventar informacoes.
3. Informe o nivel de cautela com base nas metricas.
4. Liste limitacoes do modelo.
5. Termine reforcando que a decisao final e de um profissional de saude.

Formato:
- Resumo clinico em ate 5 linhas.
- Fatores principais em bullets.
- Limitacoes em bullets.
- Recomendacao de uso seguro.
"""


def mock_llm_response(request: LLMExplanationRequest) -> str:
    predicted_text = "maior risco estimado de SOP" if request.predicted_label == 1 else "menor risco estimado de SOP"
    top_features = ", ".join(request.top_features[:5])
    recall = request.model_metrics.get("recall_pos", 0)
    auc = request.model_metrics.get("auc_roc", 0)

    return f"""Resumo clinico:
O modelo indicou {predicted_text}, com probabilidade estimada de SOP de {request.probability_pcos:.1%}. Esse resultado deve ser interpretado como apoio a triagem, nao como diagnostico definitivo. O desempenho global sugere boa capacidade discriminativa, com recall da classe positiva de {recall:.1%} e AUC-ROC de {auc:.3f}. A decisao final deve considerar avaliacao medica, exames e contexto clinico completo.

Fatores principais:
- As variaveis mais relevantes no modelo foram: {top_features}.
- Features ligadas a foliculos, sintomas e marcadores hormonais sao coerentes com a literatura sobre SOP.
- A probabilidade estimada ajuda a priorizar investigacao, mas nao substitui criterio clinico.

Limitacoes:
- O dataset e pequeno e vem de uma populacao especifica.
- O modelo foi treinado com dados historicos e precisa de validacao prospectiva.
- A explicacao resume sinais estatisticos do modelo, nao causalidade medica.

Recomendacao de uso seguro:
Use o resultado como sinal de triagem para apoiar conversa clinica e eventual investigacao adicional com profissional de saude."""


def evaluate_response_safety(response: str) -> dict[str, bool]:
    lowered = response.lower()
    forbidden_terms = [
        "prescrevo",
        "tomar medicamento",
        "inicie tratamento",
    ]
    definitive_diagnosis = (
        ("diagnostico definitivo" in lowered or "diagnóstico definitivo" in lowered)
        and "nao como diagnostico definitivo" not in lowered
        and "não como diagnóstico definitivo" not in lowered
        and "nao forneca diagnostico definitivo" not in lowered
        and "não forneça diagnóstico definitivo" not in lowered
    )
    return {
        "mentions_triage_support": "triagem" in lowered or "apoio" in lowered,
        "avoids_forbidden_terms": not definitive_diagnosis
        and not any(term in lowered for term in forbidden_terms),
        "mentions_professional": "profissional" in lowered or "medic" in lowered,
    }


def generate_explanation(request: LLMExplanationRequest) -> tuple[str, dict[str, bool]]:
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()

    # O provider real fica isolado para manter os testes e a demo reproduziveis.
    # Sem chave configurada, a explicacao mock permite demonstrar prompt,
    # formato e regras de seguranca sem enviar dados sensiveis para terceiros.
    if provider == "mock" or not os.getenv("LLM_API_KEY"):
        response = mock_llm_response(request)
        return response, evaluate_response_safety(response)

    raise NotImplementedError(
        "Provider real de LLM ainda nao configurado. Use LLM_PROVIDER=mock para a demo local."
    )
