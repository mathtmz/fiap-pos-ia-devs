from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_CODE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_CODE_DIR / "outputs" / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(PROJECT_CODE_DIR / "src"))

from pcos_fase2.advanced_tuning import (
    AdvancedTuningConfig,
    advanced_history_to_frame,
    build_tuned_model,
    run_advanced_tuning,
    strip_search_only_genes,
)
from pcos_fase2.config import FIGURES_DIR, METRICS_DIR, ensure_output_dirs
from pcos_fase2.data import prepare_data
from pcos_fase2.evaluation import evaluate_classifier_with_threshold
from pcos_fase2.models import train_baselines


THRESHOLDS = [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]


def plot_advanced_history(history: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    for experiment, group in history.groupby("experiment"):
        plt.plot(group["generation"], group["best_fitness"], marker="o", label=f"{experiment} - melhor")
        plt.plot(group["generation"], group["mean_fitness"], linestyle="--", label=f"{experiment} - media")
    plt.title("Tuning avancado: evolucao do fitness")
    plt.xlabel("Geracao")
    plt.ylabel("Fitness")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "advanced_tuning_fitness.png", dpi=150)
    plt.close()


def run_threshold_sweep(models: dict[str, object], prepared) -> pd.DataFrame:
    rows = []
    for model_name, model in models.items():
        model.fit(prepared.x_train_scaled, prepared.y_train)
        for threshold in THRESHOLDS:
            metrics = evaluate_classifier_with_threshold(
                model,
                prepared.x_test_scaled,
                prepared.y_test,
                threshold,
            )
            row = metrics.as_dict()
            row["model"] = model_name
            row["threshold"] = threshold
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    ensure_output_dirs()
    prepared = prepare_data()
    baseline_models, baseline_metrics = train_baselines(prepared)

    configs = [
        AdvancedTuningConfig(
            name="GA-Tuning-Recall-Clinico",
            objective="clinical_recall",
        ),
        AdvancedTuningConfig(
            name="GA-Tuning-Balanceado",
            objective="balanced",
        ),
    ]

    results = [run_advanced_tuning(prepared, config=config) for config in configs]
    history = pd.concat([advanced_history_to_frame(result) for result in results], ignore_index=True)
    history.to_csv(METRICS_DIR / "advanced_tuning_history.csv", index=False)
    plot_advanced_history(history)

    rows = []
    for name, metrics in baseline_metrics.items():
        row = metrics.as_dict()
        row["model"] = f"baseline_{name}"
        row["threshold"] = 0.50
        rows.append(row)

    threshold_sweep = run_threshold_sweep(baseline_models, prepared)
    threshold_sweep.to_csv(METRICS_DIR / "advanced_threshold_sweep.csv", index=False)
    best_threshold_rows = (
        threshold_sweep.sort_values(
            ["f1_pos", "recall_pos", "accuracy"],
            ascending=[False, False, False],
        )
        .groupby("model", as_index=False)
        .head(1)
    )
    for _, best_threshold in best_threshold_rows.iterrows():
        row = best_threshold.to_dict()
        row["model"] = f"threshold_tuning_{row['model']}"
        rows.append(row)

    summaries = []
    for result in results:
        best = result.best_individual
        model = build_tuned_model(best.model_family, best.genes)
        _, threshold = strip_search_only_genes(best.genes)
        model.fit(prepared.x_train_scaled, prepared.y_train)
        tuned_metrics = evaluate_classifier_with_threshold(
            model,
            prepared.x_test_scaled,
            prepared.y_test,
            threshold,
        )

        tuned_row = tuned_metrics.as_dict()
        tuned_row["model"] = result.config.name
        tuned_row["model_family"] = best.model_family
        tuned_row["threshold"] = threshold
        tuned_row["genes"] = json.dumps(best.genes, sort_keys=True)
        rows.append(tuned_row)

        summaries.append(
            {
                "experiment": result.config.name,
                "objective": result.config.objective,
                "elapsed_seconds": result.elapsed_seconds,
                "best_model_family": best.model_family,
                "best_genes": best.genes,
                "cv_metrics": best.cv_metrics.as_dict(),
                "test_metrics": tuned_metrics.as_dict(),
            }
        )

    comparison = pd.DataFrame(rows)
    comparison.to_csv(METRICS_DIR / "advanced_tuning_comparison.csv", index=False)

    (METRICS_DIR / "advanced_tuning_summary.json").write_text(
        json.dumps(summaries, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=== Tuning avancado ===")
    for summary in summaries:
        print(f"{summary['experiment']}: {summary['best_model_family']} {summary['best_genes']}")
    print("\n=== Comparativo no teste ===")
    print(comparison.drop(columns=["confusion_matrix"], errors="ignore").to_string(index=False))


if __name__ == "__main__":
    main()
