import json
import math
import re
from collections import Counter
from pathlib import Path

from .config import CORPUS_FILE, RETRIEVAL_K

TOKEN = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)


def load_corpus(path: Path = CORPUS_FILE) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError("Corpus não encontrado. Execute scripts/ingest_corpus.py.")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def retrieve(question: str, k: int = RETRIEVAL_K, path: Path = CORPUS_FILE) -> list[dict]:
    query = Counter(token.lower() for token in TOKEN.findall(question))
    scored: list[tuple[float, dict]] = []
    for chunk in load_corpus(path):
        terms = Counter(token.lower() for token in TOKEN.findall(chunk["text"]))
        numerator = sum(query[word] * terms[word] for word in query)
        denominator = math.sqrt(sum(value * value for value in query.values()) * sum(value * value for value in terms.values()))
        score = numerator / denominator if denominator else 0.0
        if score > 0:
            chunk["score"] = round(score, 4)
            scored.append((score, chunk))
    return [item for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:k]]
