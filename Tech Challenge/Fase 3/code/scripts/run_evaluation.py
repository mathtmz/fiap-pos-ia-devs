"""Evaluate retrieval on versioned demo and official-source reference questions."""
import json
import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_ROOT.parent
sys.path.insert(0, str(CODE_ROOT / "src"))

from pcos_fase3.retrieval import retrieve

CASES_FILE = PROJECT_ROOT / "data" / "eval" / "retrieval_cases.jsonl"
OUTPUT_FILE = CODE_ROOT / "outputs" / "metrics" / "retrieval_metrics.json"


def evaluate_retrieval(cases: list[dict], k: int = 3) -> tuple[dict, list[dict]]:
    if not cases:
        raise ValueError("O conjunto de avaliação de retrieval está vazio.")
    if k < 1:
        raise ValueError("k precisa ser maior que zero.")

    precision_scores = []
    recall_scores = []
    reciprocal_ranks = []
    per_case = []
    for case in cases:
        relevant = set(case["relevant_source_ids"])
        retrieved = retrieve(case["question"], k=k)
        retrieved_ids = [item["source_id"] for item in retrieved]
        hits = relevant.intersection(retrieved_ids)
        first_relevant_rank = next(
            (rank for rank, source_id in enumerate(retrieved_ids, 1) if source_id in relevant),
            None,
        )
        precision_scores.append(len(hits) / k)
        recall_scores.append(len(hits) / len(relevant) if relevant else 0.0)
        reciprocal_ranks.append(1 / first_relevant_rank if first_relevant_rank else 0.0)
        per_case.append(
            {
                "id": case["id"],
                "retrieved_source_ids": retrieved_ids,
                "relevant_source_ids": sorted(relevant),
                "precision_at_k": precision_scores[-1],
                "recall_at_k": recall_scores[-1],
                "reciprocal_rank": reciprocal_ranks[-1],
            }
        )
    metrics = {
        "k": k,
        "case_count": len(cases),
        "precision_at_3": sum(precision_scores) / len(cases),
        "recall_at_3": sum(recall_scores) / len(cases),
        "mrr": sum(reciprocal_ranks) / len(cases),
        "retriever": "weighted lexical cosine over text, titles, and curated keywords",
        "note": (
            "Avaliação de recuperação de engenharia sobre notas de demonstração e resumos "
            "parafraseados de fontes oficiais; não representa desempenho clínico nem valida "
            "os resumos para decisões individuais."
        ),
    }
    return metrics, per_case


def main() -> None:
    cases = [
        json.loads(line)
        for line in CASES_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    metrics, per_case = evaluate_retrieval(cases, k=3)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(
            {"metrics": metrics, "per_case": per_case},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
