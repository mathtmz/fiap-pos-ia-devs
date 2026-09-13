import re

from .config import MAX_QUESTION_LENGTH

PII_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.I),
    re.compile(r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9?\d{4}[-\s]?\d{4}\b"),
    re.compile(r"\b\d{3}\.?(?:\d{3})\.?(?:\d{3})-?\d{2}\b"),
)
INJECTION = re.compile(r"ignore\s+(?:as\s+)?(?:instru[çc][õo]es|instructions)|system\s+prompt|reveal\s+(?:the\s+)?prompt|jailbreak", re.I)
PROHIBITED = re.compile(r"\b(?:prescrev(?:a|er)|receita|dosagem|dose|diagnostic(?:o|ar)|tratamento\s+individual|medica[çc][ãa]o)\b", re.I)


def safety_decision(question: str) -> str | None:
    if len(question) > MAX_QUESTION_LENGTH:
        return "A pergunta excede o limite aceito para esta demonstração."
    if any(pattern.search(question) for pattern in PII_PATTERNS):
        return "Não envie dados pessoais ou identificadores. Este ambiente aceita apenas dados sintéticos."
    if INJECTION.search(question):
        return "Não posso seguir instruções que tentem alterar as regras do assistente."
    if PROHIBITED.search(question):
        return "Não forneço diagnóstico definitivo, prescrição, dose ou tratamento individual. Procure avaliação profissional."
    return None


def validate_answer(answer: str, sources: list[dict]) -> str | None:
    if not sources:
        return "Não há fontes recuperadas para sustentar a resposta."
    if "[" not in answer or "]" not in answer:
        return "A resposta não contém citação rastreável."
    return None
