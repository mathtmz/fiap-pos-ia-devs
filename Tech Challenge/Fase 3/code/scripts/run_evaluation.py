import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pcos_fase3.retrieval import retrieve

CASES = [{"question": "Quais são os limites do assistente?", "relevant": "SYN-FAQ-001"}, {"question": "Quais são as pendências simuladas?", "relevant": "SYN-PROTO-002"}]

if __name__ == "__main__":
    ranks = []
    for case in CASES:
        ids = [item["source_id"] for item in retrieve(case["question"])]
        ranks.append(ids.index(case["relevant"]) + 1 if case["relevant"] in ids else None)
    found = [rank for rank in ranks if rank]
    metrics = {"precision_at_3": len(found) / (len(CASES) * 3), "recall_at_3": len(found) / len(CASES), "mrr": sum(1 / rank for rank in found) / len(CASES), "note": "Métricas do corpus sintético mínimo; não são desempenho clínico."}
    output = ROOT / "outputs" / "metrics" / "retrieval_metrics.json"
    output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(metrics)
