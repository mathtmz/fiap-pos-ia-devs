from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_CODE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_CODE_DIR / "outputs" / ".matplotlib"))

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(PROJECT_CODE_DIR / "src"))

from pcos_fase2.config import FIGURES_DIR, METRICS_DIR, MODELS_DIR, ensure_output_dirs
from pcos_fase2.data import prepare_data
from pcos_fase2.evaluation import evaluate_classifier
from pcos_fase2.explainability import feature_importance_frame, permutation_importance_frame
from pcos_fase2.genetic_optimizer import (
    GeneticExperimentConfig,
    history_to_frame,
    run_genetic_experiment,
)
from pcos_fase2.models import build_model_from_chromosome, train_baselines


EXPERIMENTS = [
    GeneticExperimentConfig("GA-Exploratorio", 20, 20, 0.25, 0.80),
    GeneticExperimentConfig("GA-Balanceado", 30, 30, 0.15, 0.75),
    GeneticExperimentConfig("GA-Conservador", 20, 40, 0.08, 0.65),
]


def plot_fitness(history: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    for experiment_name, group in history.groupby("experiment"):
        plt.plot(group["generation"], group["best_fitness"], marker="o", label=f"{experiment_name} - melhor")
        plt.plot(group["generation"], group["mean_fitness"], linestyle="--", alpha=0.7, label=f"{experiment_name} - media")
    plt.title("Evolucao do fitness por geracao")
    plt.xlabel("Geracao")
    plt.ylabel("Fitness")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fitness_evolution.png", dpi=150)
    plt.close()


def main() -> None:
    ensure_output_dirs()
    prepared = prepare_data()
    _, baseline_metrics = train_baselines(prepared)

    results = []
    for config in EXPERIMENTS:
        result = run_genetic_experiment(
            prepared,
            model_family="random_forest",
            config=config,
            log_path=METRICS_DIR / f"{config.name}.jsonl",
        )
        results.append(result)
        print(
            f"{config.name}: best_fitness={result.best_individual.fitness:.4f} "
            f"genes={result.best_individual.genes}"
        )

    history = history_to_frame(results)
    history.to_csv(METRICS_DIR / "ga_history.csv", index=False)
    plot_fitness(history)

    best_result = max(results, key=lambda item: item.best_individual.fitness)
    best_model = build_model_from_chromosome(
        best_result.model_family,
        best_result.best_individual.genes,
    )
    best_model.fit(prepared.x_train_scaled, prepared.y_train)
    best_metrics = evaluate_classifier(best_model, prepared.x_test_scaled, prepared.y_test)

    comparison_rows = []
    for name, metrics in baseline_metrics.items():
        row = metrics.as_dict()
        row["model"] = f"baseline_{name}"
        comparison_rows.append(row)
    optimized_row = best_metrics.as_dict()
    optimized_row["model"] = f"optimized_{best_result.config.name}"
    optimized_row["genes"] = json.dumps(best_result.best_individual.genes, sort_keys=True)
    comparison_rows.append(optimized_row)

    comparison = pd.DataFrame(comparison_rows)
    comparison.to_csv(METRICS_DIR / "model_comparison.csv", index=False)

    joblib.dump(
        {
            "model": best_model,
            "scaler": prepared.scaler,
            "feature_names": prepared.feature_names,
            "genes": best_result.best_individual.genes,
            "metrics": best_metrics.as_dict(),
        },
        MODELS_DIR / "best_model.joblib",
    )

    importance = feature_importance_frame(best_model, prepared.feature_names)
    importance.to_csv(METRICS_DIR / "feature_importance.csv", index=False)
    permutation = permutation_importance_frame(
        best_model, prepared.x_test_scaled, prepared.y_test, prepared.feature_names
    )
    permutation.to_csv(METRICS_DIR / "permutation_importance.csv", index=False)

    print("\n=== Comparativo final ===")
    print(comparison.drop(columns=["confusion_matrix"], errors="ignore").to_string(index=False))
    print(f"\nMelhor modelo salvo em: {MODELS_DIR / 'best_model.joblib'}")


if __name__ == "__main__":
    main()
