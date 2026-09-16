"""Small weighted lexical retriever for the local Portuguese corpus."""
from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

from .config import CORPUS_FILE, RETRIEVAL_K

TOKEN = re.compile(r"\w+", re.UNICODE)
STOPWORDS = frozenset(
    "a ao aos aquela aquelas aquele aqueles aquilo as até com como da das de dela delas "
    "dele deles depois do dos e ela elas ele eles em entre essa essas esse esses esta estas "
    "este estes eu foi foram há isso isto já lhe lhes mais mas me mesmo meu meus minha minhas "
    "muito na nas nem no nos nossa nossas nosso nossos num numa o os ou para pela pelas pelo "
    "pelos por qual quando que quem se sem seu seus sua suas também te tem temos ter teu teus "
    "toda todas todo todos tu um uma umas uns você vocês não sim onde este esta pode devem "
    "deve sistema assistente resposta protótipo pergunta sobre fazer explique como lida".split()
)


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _tokens(text: str) -> list[str]:
    return [token for token in TOKEN.findall(_normalize(text)) if token not in STOPWORDS and len(token) > 1]


def load_corpus(path: Path = CORPUS_FILE) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError("Corpus não encontrado. Execute scripts/ingest_corpus.py.")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _weighted_document_terms(document: dict) -> Counter[str]:
    terms: Counter[str] = Counter()
    for token in _tokens(document.get("text", "")):
        terms[token] += 1.0
    for token in _tokens(document.get("title", "")):
        terms[token] += 3.0
    for token in _tokens(document.get("source_id", "")):
        terms[token] += 1.5
    for keyword in document.get("keywords", []):
        for token in _tokens(keyword):
            terms[token] += 2.5
    return terms


def retrieve(question: str, k: int = RETRIEVAL_K, path: Path = CORPUS_FILE) -> list[dict]:
    if k < 1:
        raise ValueError("k precisa ser maior que zero.")
    query = Counter(_tokens(question))
    if not query:
        return []

    scored: list[tuple[float, dict]] = []
    for chunk in load_corpus(path):
        terms = _weighted_document_terms(chunk)
        numerator = sum(query[word] * terms[word] for word in query)
        denominator = math.sqrt(
            sum(value * value for value in query.values())
            * sum(value * value for value in terms.values())
        )
        score = numerator / denominator if denominator else 0.0
        if score > 0:
            result = dict(chunk)
            result["score"] = round(score, 4)
            scored.append((score, result))
    return [item for _, item in sorted(scored, key=lambda pair: (-pair[0], pair[1]["source_id"]))[:k]]
