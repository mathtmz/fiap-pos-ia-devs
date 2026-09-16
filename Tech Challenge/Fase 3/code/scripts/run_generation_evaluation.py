"""Compare base/LoRA generation with and without retrieved synthetic evidence."""
import argparse
import gc
import json
import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_ROOT.parent
sys.path.insert(0, str(CODE_ROOT / "src"))

from pcos_fase3.config import MODEL_ADAPTER_DIR
from pcos_fase3.generation import load_local_generator
from pcos_fase3.retrieval import retrieve

TEST_FILE = PROJECT_ROOT / "data" / "processed" / "instruction" / "test.jsonl"
OUTPUT_FILE = CODE_ROOT / "outputs" / "metrics" / "generation_comparison.jsonl"


def user_and_expected(row: dict) -> tuple[str, str]:
    question = next(
        message["content"] for message in row["messages"] if message["role"] == "user"
    )
    expected = next(
        message["content"]
        for message in reversed(row["messages"])
        if message["role"] == "assistant"
    )
    return question, expected


def run_comparison(limit: int = 90, local_files_only: bool = False) -> list[dict]:
    if not (MODEL_ADAPTER_DIR / "adapter_config.json").is_file():
        raise FileNotFoundError(
            f"Adaptador não encontrado em {MODEL_ADAPTER_DIR}; execute o fine-tuning primeiro."
        )
    rows = [
        json.loads(line)
        for line in TEST_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ][:limit]
    if not rows:
        raise ValueError("O conjunto de teste instrucional está vazio.")
    outputs = {
        row["metadata"]["id"]: {
            "id": row["metadata"]["id"],
            "topic": row["metadata"]["topic"],
            "question": user_and_expected(row)[0],
            "reference": user_and_expected(row)[1],
            "source_ids": [],
            "base_without_rag": "",
            "lora_without_rag": "",
            "lora_with_rag": "",
            "manual_review": {
                "faithfulness_1_to_5": None,
                "completeness_1_to_5": None,
                "clarity_1_to_5": None,
                "safety_pass": None,
                "review_notes": "",
            },
        }
        for row in rows
    }

    stages = (
        ("base_without_rag", False, False),
        ("lora_without_rag", True, False),
        ("lora_with_rag", True, True),
    )
    for output_key, use_adapter, use_rag in stages:
        generator = load_local_generator(
            use_adapter=use_adapter, local_files_only=local_files_only
        )
        for row in rows:
            question, _ = user_and_expected(row)
            sources = retrieve(question) if use_rag else []
            result = generator(
                {
                    "question": question,
                    "patient": {"available": False},
                    "sources": sources,
                }
            )
            record = outputs[row["metadata"]["id"]]
            record[output_key] = result
            if use_rag:
                record["source_ids"] = [source["source_id"] for source in sources]
        del generator
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
    return list(outputs.values())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=90)
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE)
    args = parser.parse_args()
    results = run_comparison(args.limit, args.local_files_only)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in results) + "\n",
        encoding="utf-8",
    )
    print(f"{len(results)} casos salvos em {args.output}")
    print("Preencha a rubrica manual_review antes de consolidar os resultados no relatório.")


if __name__ == "__main__":
    main()
