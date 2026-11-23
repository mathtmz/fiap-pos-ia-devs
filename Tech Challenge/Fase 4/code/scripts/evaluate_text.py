"""Evaluate Qwen sentiment, term extraction and review routing on fixed cases."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
sys.path.insert(0, str(CODE_DIR / "src"))

from fisio_fase4.audio_text import analyze_text, literal_match, route_text_events


TERM_ALIASES = {
    "dor": ("dor", "pain"),
    "cansaço": ("cansaço", "cansaco", "fadiga", "fatigue"),
    "falta_de_ar": (
        "falta de ar",
        "dispneia",
        "dificuldade de respirar",
        "shortness of breath",
    ),
}
SENTIMENTS = ("positivo", "negativo", "neutro")


def binary_metrics(truth, prediction):
    tp = sum(expected and actual for expected, actual in zip(truth, prediction))
    fp = sum((not expected) and actual for expected, actual in zip(truth, prediction))
    fn = sum(expected and (not actual) for expected, actual in zip(truth, prediction))
    tn = sum((not expected) and (not actual) for expected, actual in zip(truth, prediction))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def predicted_terms(model_terms):
    text = " ".join(model_terms).casefold()
    return {
        category
        for category, aliases in TERM_ALIASES.items()
        if any(literal_match(alias, text) for alias in aliases)
    }


def evaluate(dataset_path, model_name="Qwen/Qwen2.5-0.5B-Instruct"):
    dataset = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    rows = []
    started = time.perf_counter()
    for case in dataset["cases"]:
        before = time.perf_counter()
        try:
            analysis = analyze_text(case["text"], model_name=model_name)
            routed_events, review_items = route_text_events(
                analysis,
                [{"start": 0.0, "end": 1.0, "text": case["text"]}],
                f"texto_{case['id']}",
            )
            output_status = analysis.get("status", "erro")
            actual_terms = sorted(predicted_terms(analysis.get("terms", [])))
            actual_sentiment = analysis.get("sentiment", "indeterminado")
            actual_alert = bool(routed_events)
            actual_review = bool(review_items)
        except Exception as exc:
            analysis = {"sentiment": "indeterminado", "terms": [], "error": str(exc)}
            output_status = "erro"
            actual_terms, actual_sentiment = [], "indeterminado"
            actual_alert, actual_review = False, False
        rows.append(
            {
                "id": case["id"],
                "text": case["text"],
                "expected_sentiment": case["expected_sentiment"],
                "actual_sentiment": actual_sentiment,
                "expected_terms": case["expected_terms"],
                "actual_terms": actual_terms,
                "expected_alert": case["expected_alert"],
                "actual_alert": actual_alert,
                "expected_review": case["expected_review"],
                "actual_review": actual_review,
                "status": output_status,
                "seconds": round(time.perf_counter() - before, 3),
                "model_output": analysis,
            }
        )

    sentiment_rows = [
        row for row in rows if row["actual_sentiment"] in SENTIMENTS
    ]
    sentiment_by_class = {}
    for label in SENTIMENTS:
        truth = [row["expected_sentiment"] == label for row in sentiment_rows]
        prediction = [row["actual_sentiment"] == label for row in sentiment_rows]
        sentiment_by_class[label] = binary_metrics(truth, prediction)
    term_metrics = {}
    for label in TERM_ALIASES:
        truth = [label in row["expected_terms"] for row in rows]
        prediction = [label in row["actual_terms"] for row in rows]
        term_metrics[label] = binary_metrics(truth, prediction)
    result = {
        "dataset": dataset["dataset"],
        "dataset_version": dataset["version"],
        "model": model_name,
        "case_count": len(rows),
        "sentiment_accuracy": round(
            sum(row["expected_sentiment"] == row["actual_sentiment"] for row in rows)
            / len(rows),
            4,
        ),
        "sentiment_macro_f1": round(
            sum(item["f1"] for item in sentiment_by_class.values()) / len(SENTIMENTS),
            4,
        ),
        "sentiment_by_class": sentiment_by_class,
        "terms_by_class": term_metrics,
        "alert_routing": binary_metrics(
            [row["expected_alert"] for row in rows],
            [row["actual_alert"] for row in rows],
        ),
        "human_review_routing": binary_metrics(
            [row["expected_review"] for row in rows],
            [row["actual_review"] for row in rows],
        ),
        "elapsed_s": round(time.perf_counter() - started, 3),
        "cases": rows,
        "limitation": "Frases sintéticas fixas; resultados não validam interpretação clínica nem generalização para consultas reais.",
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=PROJECT_ROOT / "data/synthetic/text_evaluation_cases.json",
    )
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "docs/resultados/text_evaluation.json",
    )
    args = parser.parse_args()
    result = evaluate(args.dataset, args.model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "sentiment_accuracy": result["sentiment_accuracy"],
                "sentiment_macro_f1": result["sentiment_macro_f1"],
                "alert_f1": result["alert_routing"]["f1"],
                "review_f1": result["human_review_routing"]["f1"],
                "elapsed_s": result["elapsed_s"],
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
