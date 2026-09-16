import re

from .config import MAX_QUESTION_LENGTH

CLINICIAN_REVIEW_NOTICE = (
    "RASCUNHO DE APOIO — não é ordem médica. Toda hipótese diagnóstica, prescrição "
    "ou dose exige avaliação e validação pelo médico responsável, que mantém a "
    "decisão clínica final. Não comunique esta saída ao paciente sem mediação médica."
)

CLINICAL_SUPPORT_ABSTENTION = (
    "Pedido recebido, mas as fontes disponíveis não têm validação clínica suficiente "
    "para sustentar diagnóstico, prescrição ou dose individual. "
    "Consulte fontes clínicas aprovadas e encaminhe a decisão ao médico responsável.\n\n"
    + CLINICIAN_REVIEW_NOTICE
)

PII_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.I),
    re.compile(r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9?\d{4}[-\s]?\d{4}\b"),
    re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
)
INJECTION = re.compile(
    r"ignore\s+(?:as\s+)?(?:instruções|instrucoes|instructions)|"
    r"system\s+prompt|reveal\s+(?:the\s+)?prompt|jailbreak",
    re.I,
)
INDIVIDUAL_CLINICAL_REQUEST = re.compile(
    r"\b(?:diagnostique|diagnosticar|prescreva|prescrever|receite|receitar)\b|"
    r"\b(?:faça|faca|sugira|recomende|indique|proponha|qual|que)\b.{0,80}\b"
    r"(?:hip[oó]tese\s+diagn[oó]stica|diagn[oó]stico|prescri(?:ção|cao)|dose|dosagem|tratamento)\b|"
    r"\b(?:hip[oó]tese\s+diagn[oó]stica|diagn[oó]stico|prescri(?:ção|cao)|dose|dosagem|tratamento)\b"
    r".{0,80}\b(?:para mim|devo|sugira|recomende|indique|qual seria)\b",
    re.I,
)

# Outputs that amount to individual clinical conclusions or instructions need a
# cited source explicitly validated for clinical use and individual decisions.
# Source authority alone does not satisfy either condition.
CLINICAL_OUTPUT_PATTERNS = (
    re.compile(
        r"\b(?:você|o paciente|a paciente)\s+(?:tem|apresenta|possui|está com)\s+(?:sop|pcos)\b|"
        r"\b(?:seu|o)\s+diagnóstico\s+(?:é|eh|está confirmado)|"
        r"\b(?:hipótese|diagnóstico)\s+(?:mais\s+provável\s+)?(?:é|eh)\s+(?:sop|pcos)\b",
        re.I,
    ),
    re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:mg|mcg|μg|µg|g|ml|mL|UI|unidades?|comprimidos?|gotas)\b", re.I),
    re.compile(
        r"\b(?:prescreva|prescrevo|receite|receito|tome|inicie|administre|"
        r"suspenda|aumente|reduza|use|utilize)\b.{0,100}\b(?:dose|medicação|medicamento|"
        r"remédio|tratamento|mg|mcg|comprimido|gotas)\b",
        re.I,
    ),
)
CLINICAL_OUTPUT_PATTERNS += (
    re.compile(
        r"\b(?:hipótese\s+diagnóstica|diagnóstico)\s*"
        r"(?::|\s+(?:provável|possível|seria|é|indica|sugere))",
        re.I,
    ),
    re.compile(r"\b(?:hipótese\s+diagnóstica|diagnóstico)\b\s*:?\s*(?:de\s+)?(?:SOP|PCOS)\b", re.I),
    re.compile(r"\b(?:hipótese|diagnóstico)\s*:\s*(?:SOP|PCOS)\b", re.I),
    re.compile(r"\b(?:prescreva|prescrevo|receite|receito)\b", re.I),
    re.compile(r"\bprescri(?:ção|cao)\s*:\s*\S+", re.I),
)


def safety_decision(question: str) -> str | None:
    """Block privacy/injection risks but let clinical requests reach review."""
    if len(question) > MAX_QUESTION_LENGTH:
        return "A pergunta excede o limite aceito para esta demonstração."
    if any(pattern.search(question) for pattern in PII_PATTERNS):
        return "Não envie dados pessoais ou identificadores. Este ambiente aceita apenas dados de demonstração."
    if INJECTION.search(question):
        return "Não posso seguir instruções que tentem alterar as regras do assistente."
    return None


def is_individual_clinical_request(question: str) -> bool:
    """Identify requests for an individual clinical conclusion or action."""
    return bool(INDIVIDUAL_CLINICAL_REQUEST.search(question))


def add_clinician_notice(answer: str) -> str:
    if CLINICIAN_REVIEW_NOTICE in answer:
        return answer
    return f"{answer.rstrip()}\n\n{CLINICIAN_REVIEW_NOTICE}"


def validate_answer(answer: str, sources: list[dict]) -> str | None:
    if not sources:
        return add_clinician_notice("Não há fontes recuperadas para sustentar a resposta.")

    cited_ids = set(re.findall(r"\[([A-Z0-9_-]+)\]", answer))
    available = {source.get("source_id"): source for source in sources}
    if not cited_ids:
        return add_clinician_notice("A resposta não contém citação rastreável.")
    if not cited_ids.issubset(available):
        return add_clinician_notice("A resposta citou uma fonte que não foi recuperada.")
    if CLINICIAN_REVIEW_NOTICE not in answer:
        return add_clinician_notice("A resposta foi omitida porque faltou o aviso obrigatório de revisão médica.")

    answer_content = answer.replace(CLINICIAN_REVIEW_NOTICE, "")
    has_individual_clinical_output = any(
        pattern.search(answer_content) for pattern in CLINICAL_OUTPUT_PATTERNS
    )
    cited_sources = [available[source_id] for source_id in cited_ids]
    has_validated_clinical_source = bool(cited_sources) and all(
        source.get("clinical_validated") is True
        and source.get("supports_individual_decisions") is True
        for source in cited_sources
    )
    if has_individual_clinical_output and not has_validated_clinical_source:
        return CLINICAL_SUPPORT_ABSTENTION
    return None
