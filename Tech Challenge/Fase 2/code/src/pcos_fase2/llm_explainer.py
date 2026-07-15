from __future__ import annotations

import json
import os
import ssl
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass

import certifi


SYSTEM_RULES = """Voce e um assistente de apoio a interpretacao de modelos de machine learning em saude.
Nao forneca diagnostico definitivo, prescricao ou conduta medica.
Explique os resultados como apoio a triagem clinica e recomende avaliacao profissional quando adequado."""


# Mapeia cada coluna do dataset PCOS para termos clinicos equivalentes em
# portugues. E usado para reconhecer que a LLM se referiu a um fator real do
# modelo mesmo quando traduz ou parafraseia o nome tecnico da coluna, em vez
# de citar o nome em ingles literalmente.
FEATURE_SYNONYMS: dict[str, list[str]] = {
    "Age (yrs)": ["idade"],
    "Weight (Kg)": ["peso"],
    "Height(Cm)": ["altura"],
    "BMI": ["imc"],
    "Pulse rate(bpm)": ["pulso", "frequencia cardiaca"],
    "Hb(g/dl)": ["hemoglobina"],
    "Cycle(R/I)": ["ciclo menstrual", "ciclo"],
    "Cycle length(days)": ["duracao do ciclo", "ciclo"],
    "Marraige Status (Yrs)": ["tempo de casamento", "casamento"],
    "No. of aborptions": ["aborto"],
    "LH(mIU/mL)": ["lh"],
    "Hip(inch)": ["quadril"],
    "Waist(inch)": ["cintura"],
    "AMH(ng/mL)": ["amh"],
    "Vit D3 (ng/mL)": ["vitamina d", "vit d"],
    "Weight gain(Y/N)": ["ganho de peso"],
    "hair growth(Y/N)": ["crescimento de pelo", "pelo", "hirsutismo"],
    "Skin darkening (Y/N)": ["escurecimento da pele", "acantose"],
    "Hair loss(Y/N)": ["queda de cabelo", "alopecia"],
    "Pimples(Y/N)": ["acne", "espinha"],
    "Fast food (Y/N)": ["fast food", "alimentacao"],
    "Reg.Exercise(Y/N)": ["exercicio", "atividade fisica"],
    "Follicle No. (L)": ["foliculo"],
    "Follicle No. (R)": ["foliculo"],
    "Avg. F size (L) (mm)": ["tamanho folicular", "tamanho do foliculo"],
    "Avg. F size (R) (mm)": ["tamanho folicular", "tamanho do foliculo"],
    "Endometrium (mm)": ["endometrio"],
    "total_foliculos": ["foliculo"],
    "soma_sintomas": ["sintoma"],
    "faixa_imc": ["imc"],
    "razao_lh_fsh": ["lh", "fsh"],
}


def _normalize_text(text: str) -> str:
    """Remove acentuacao e normaliza para minusculas, para comparar termos em
    portugues (ex.: "foliculo" vs "folículo") sem falso negativo por acento.
    """
    without_accents = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return without_accents.lower()


def _feature_terms(feature: str) -> list[str]:
    """Retorna os termos aceitos para considerar que a LLM se referiu a uma
    feature: o nome tecnico normalizado (fallback) e os sinonimos clinicos
    conhecidos, quando existentes.
    """
    normalized_feature = feature.strip()
    synonyms = FEATURE_SYNONYMS.get(normalized_feature)
    if synonyms:
        return synonyms
    return [normalized_feature]


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


def evaluate_response_quality(request: LLMExplanationRequest, response: str) -> dict[str, bool]:
    """Avalia a qualidade da explicacao gerada, em complemento a checagem de
    seguranca feita por `evaluate_response_safety`.

    Este e um criterio automatico e objetivo, pensado para revisao humana
    posterior: confere se a resposta e consistente com os dados enviados na
    requisicao e se cobre a estrutura pedida no prompt, sem exigir uma
    segunda chamada de LLM como avaliador.
    """
    lowered = response.lower()
    normalized_response = _normalize_text(response)

    expected_probability_dot = f"{request.probability_pcos:.1%}".lower()
    expected_probability_comma = expected_probability_dot.replace(".", ",")
    numeric_consistency = (
        expected_probability_dot in lowered or expected_probability_comma in lowered
    )

    expected_sections = ["resumo", "fatores", "limita", "recomend"]
    covers_expected_sections = all(section in lowered for section in expected_sections)

    mentions_top_features = any(
        _normalize_text(term) in normalized_response
        for feature in request.top_features
        for term in _feature_terms(feature)
    )

    return {
        "numeric_consistency": numeric_consistency,
        "covers_expected_sections": covers_expected_sections,
        "mentions_top_features": mentions_top_features,
    }


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


def openai_llm_response(request: LLMExplanationRequest) -> str:
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Defina LLM_API_KEY ou OPENAI_API_KEY para usar LLM_PROVIDER=openai.")

    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    api_url = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": build_prompt(request)},
        ],
    }

    http_request = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(http_request, timeout=45, context=ssl_context) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Falha na chamada da LLM: HTTP {error.code} - {details}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Falha de conexao com a LLM: {error.reason}") from error

    choices = response_payload.get("choices", [])
    if not choices:
        raise RuntimeError(f"Resposta da LLM sem choices: {response_payload}")
    return choices[0]["message"]["content"].strip()


def gemini_llm_response(request: LLMExplanationRequest) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError("Defina GEMINI_API_KEY ou LLM_API_KEY para usar LLM_PROVIDER=gemini.")

    model = os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")
    api_url = os.getenv(
        "GEMINI_API_URL",
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    )
    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_RULES}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": build_prompt(request)}],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
        },
    }

    separator = "&" if "?" in api_url else "?"
    url = f"{api_url}{separator}key={api_key}"
    http_request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(http_request, timeout=45, context=ssl_context) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Falha na chamada da Gemini API: HTTP {error.code} - {details}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Falha de conexao com a Gemini API: {error.reason}") from error

    candidates = response_payload.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"Resposta da Gemini API sem candidates: {response_payload}")

    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [part.get("text", "") for part in parts if part.get("text")]
    if not text_parts:
        raise RuntimeError(f"Resposta da Gemini API sem texto: {response_payload}")
    return "\n".join(text_parts).strip()


def generate_explanation(request: LLMExplanationRequest) -> tuple[str, dict[str, bool]]:
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()

    # O mock e o modo padrao para manter a demo reproduzivel e evitar envio de
    # dados clinicos para terceiros quando uma chave real nao foi configurada.
    if provider == "mock":
        response = mock_llm_response(request)
        return response, evaluate_response_safety(response)

    if provider == "openai":
        response = openai_llm_response(request)
        return response, evaluate_response_safety(response)

    if provider == "gemini":
        response = gemini_llm_response(request)
        return response, evaluate_response_safety(response)

    raise ValueError("LLM_PROVIDER deve ser 'mock', 'openai' ou 'gemini'.")
