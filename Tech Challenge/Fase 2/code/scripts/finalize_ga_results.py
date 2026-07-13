from __future__ import annotations

import ast
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
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay, confusion_matrix

sys.path.insert(0, str(PROJECT_CODE_DIR / "src"))

from pcos_fase2.config import FIGURES_DIR, METRICS_DIR, MODELS_DIR, ensure_output_dirs
from pcos_fase2.data import prepare_data
from pcos_fase2.evaluation import evaluate_classifier
from pcos_fase2.explainability import feature_importance_frame, permutation_importance_frame
from pcos_fase2.models import build_model_from_chromosome, train_baselines


def load_history_from_jsonl() -> pd.DataFrame:
    rows = []
    for path in sorted(METRICS_DIR.glob("GA-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise FileNotFoundError("Nenhum historico GA-*.jsonl encontrado.")
    return pd.DataFrame(rows)


def parse_genes(value: str) -> dict:
    return json.loads(value)


def plot_fitness(history: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    for experiment_name, group in history.groupby("experiment"):
        group = group.sort_values("generation")
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


def plot_confusion_matrix(model, prepared) -> None:
    predictions = model.predict(prepared.x_test_scaled)
    matrix = confusion_matrix(prepared.y_test, predictions)
    display = ConfusionMatrixDisplay(matrix, display_labels=["Sem SOP", "Com SOP"])
    display.plot(cmap="Blues", colorbar=False)
    plt.title("Matriz de confusao - melhor modelo GA")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "confusion_matrix.png", dpi=150)
    plt.close()


def plot_roc_curve(model, prepared) -> None:
    RocCurveDisplay.from_estimator(model, prepared.x_test_scaled, prepared.y_test)
    plt.title("Curva ROC - melhor modelo GA")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "roc_curve.png", dpi=150)
    plt.close()


def plot_feature_importance(importance: pd.DataFrame) -> None:
    top = importance.head(15).sort_values("importance")
    colors = ["#E91E63" if item == "feature_engineering" else "#607D8B" for item in top["type"]]
    plt.figure(figsize=(9, 7))
    plt.barh(top["feature"], top["importance"], color=colors)
    plt.title("Feature importance - melhor Random Forest GA")
    plt.xlabel("Importancia")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "feature_importance.png", dpi=150)
    plt.close()


def main() -> None:
    ensure_output_dirs()
    prepared = prepare_data()
    _, baseline_metrics = train_baselines(prepared)

    history = load_history_from_jsonl()
    history.to_csv(METRICS_DIR / "ga_history.csv", index=False)
    plot_fitness(history)

    best_row = history.sort_values("best_fitness", ascending=False).iloc[0]
    best_genes = parse_genes(best_row["best_genes"])
    model = build_model_from_chromosome("random_forest", best_genes)
    model.fit(prepared.x_train_scaled, prepared.y_train)
    best_metrics = evaluate_classifier(model, prepared.x_test_scaled, prepared.y_test)

    rows = []
    for name, metrics in baseline_metrics.items():
        row = metrics.as_dict()
        row["model"] = f"baseline_{name}"
        row["genes"] = ""
        rows.append(row)
    optimized_row = best_metrics.as_dict()
    optimized_row["model"] = f"optimized_{best_row['experiment']}"
    optimized_row["genes"] = json.dumps(best_genes, sort_keys=True)
    rows.append(optimized_row)
    comparison = pd.DataFrame(rows)
    comparison.to_csv(METRICS_DIR / "model_comparison.csv", index=False)

    importance = feature_importance_frame(model, prepared.feature_names)
    importance.to_csv(METRICS_DIR / "feature_importance.csv", index=False)
    permutation = permutation_importance_frame(
        model, prepared.x_test_scaled, prepared.y_test, prepared.feature_names
    )
    permutation.to_csv(METRICS_DIR / "permutation_importance.csv", index=False)

    plot_confusion_matrix(model, prepared)
    plot_roc_curve(model, prepared)
    plot_feature_importance(importance)

    joblib.dump(
        {
            "model": model,
            "scaler": prepared.scaler,
            "feature_names": prepared.feature_names,
            "genes": best_genes,
            "metrics": best_metrics.as_dict(),
        },
        MODELS_DIR / "best_model.joblib",
    )

    print("=== Melhor configuracao GA ===")
    print(best_row[["experiment", "generation", "best_fitness", "recall_pos", "f1_pos", "auc_roc", "accuracy"]].to_string())
    print(json.dumps(best_genes, indent=2, sort_keys=True))
    print("\n=== Metricas no teste ===")
    print(best_metrics)


if __name__ == "__main__":
    main()
