from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold

from .config import RANDOM_STATE
from .data import PreparedData
from .evaluation import ModelMetrics, calculate_fitness, evaluate_classifier_with_threshold
from .models import build_model_from_chromosome


ADVANCED_GENE_SPACES: dict[str, dict[str, list[Any]]] = {
    "random_forest": {
        "n_estimators": [100, 150, 200, 300, 500],
        "max_depth": [None, 5, 8, 12, 16, 24, 32],
        "min_samples_split": [2, 4, 6, 8, 10, 15],
        "min_samples_leaf": [1, 2, 3, 4, 5, 8],
        "max_features": ["sqrt", "log2", None],
        "class_weight": ["balanced", "balanced_subsample", None],
        "threshold": [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70],
    },
    "logistic_regression": {
        "C": [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0],
        "penalty": ["l1", "l2"],
        "solver": ["liblinear"],
        "class_weight": ["balanced", None],
        "max_iter": [1000, 2000, 3000],
        "threshold": [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70],
    },
}


ADVANCED_HOTSTARTS: list[dict[str, Any]] = [
    {
        "model_family": "random_forest",
        "genes": {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "max_features": "sqrt",
            "class_weight": "balanced",
            "threshold": 0.50,
        },
    },
    {
        "model_family": "random_forest",
        "genes": {
            "n_estimators": 200,
            "max_depth": 32,
            "min_samples_split": 6,
            "min_samples_leaf": 2,
            "max_features": "log2",
            "class_weight": None,
            "threshold": 0.50,
        },
    },
    {
        "model_family": "random_forest",
        "genes": {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "max_features": "sqrt",
            "class_weight": "balanced",
            "threshold": 0.60,
        },
    },
    {
        "model_family": "logistic_regression",
        "genes": {
            "C": 1.0,
            "penalty": "l2",
            "solver": "liblinear",
            "class_weight": "balanced",
            "max_iter": 1000,
            "threshold": 0.50,
        },
    },
]


@dataclass(frozen=True)
class AdvancedTuningConfig:
    name: str = "GA-Tuning-Avancado"
    population_size: int = 24
    generations: int = 24
    mutation_rate: float = 0.18
    crossover_rate: float = 0.75
    elitism_rate: float = 0.12
    tournament_size: int = 3
    patience: int = 7
    cv_splits: int = 4
    objective: str = "clinical_recall"


@dataclass
class AdvancedIndividual:
    model_family: str
    genes: dict[str, Any]
    fitness: float
    cv_metrics: ModelMetrics


@dataclass
class AdvancedTuningResult:
    config: AdvancedTuningConfig
    best_individual: AdvancedIndividual
    history: list[dict[str, Any]]
    elapsed_seconds: float


def chromosome_key(model_family: str, genes: dict[str, Any]) -> str:
    payload = {"model_family": model_family, "genes": genes}
    return json.dumps(payload, sort_keys=True, default=str)


def random_individual(rng: random.Random) -> tuple[str, dict[str, Any]]:
    model_family = rng.choice(list(ADVANCED_GENE_SPACES))
    genes = {
        gene: rng.choice(values)
        for gene, values in ADVANCED_GENE_SPACES[model_family].items()
    }
    return model_family, genes


def initial_population(
    population_size: int, rng: random.Random
) -> list[tuple[str, dict[str, Any]]]:
    population = [
        (item["model_family"], dict(item["genes"]))
        for item in ADVANCED_HOTSTARTS
    ]
    while len(population) < population_size:
        population.append(random_individual(rng))
    return population[:population_size]


def strip_search_only_genes(genes: dict[str, Any]) -> tuple[dict[str, Any], float]:
    model_genes = dict(genes)
    threshold = float(model_genes.pop("threshold"))
    return model_genes, threshold


def build_tuned_model(model_family: str, genes: dict[str, Any]):
    model_genes, _ = strip_search_only_genes(genes)
    return build_model_from_chromosome(model_family, model_genes)


def average_metrics(metrics: list[ModelMetrics]) -> ModelMetrics:
    confusion = np.sum([item.confusion_matrix for item in metrics], axis=0).astype(int).tolist()
    return ModelMetrics(
        accuracy=float(np.mean([item.accuracy for item in metrics])),
        precision_pos=float(np.mean([item.precision_pos for item in metrics])),
        recall_pos=float(np.mean([item.recall_pos for item in metrics])),
        f1_pos=float(np.mean([item.f1_pos for item in metrics])),
        auc_roc=float(np.mean([item.auc_roc for item in metrics])),
        confusion_matrix=confusion,
    )


def evaluate_cv_individual(
    prepared: PreparedData,
    model_family: str,
    genes: dict[str, Any],
    cv_splits: int,
    objective: str,
) -> AdvancedIndividual:
    model_genes, threshold = strip_search_only_genes(genes)
    splitter = StratifiedKFold(
        n_splits=cv_splits,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    fold_metrics = []
    train_metrics = []

    for train_index, valid_index in splitter.split(prepared.x_train_scaled, prepared.y_train):
        model = build_model_from_chromosome(model_family, model_genes)
        train_x = prepared.x_train_scaled[train_index]
        valid_x = prepared.x_train_scaled[valid_index]
        train_y = prepared.y_train.iloc[train_index]
        valid_y = prepared.y_train.iloc[valid_index]

        model.fit(train_x, train_y)
        fold_metrics.append(evaluate_classifier_with_threshold(model, valid_x, valid_y, threshold))
        train_metrics.append(evaluate_classifier_with_threshold(model, train_x, train_y, threshold))

    validation = average_metrics(fold_metrics)
    train = average_metrics(train_metrics)
    if objective == "balanced":
        fitness = (
            0.35 * validation.f1_pos
            + 0.25 * validation.accuracy
            + 0.25 * validation.auc_roc
            + 0.15 * validation.recall_pos
        )
        overfit_gap = train.f1_pos - validation.f1_pos
        fitness -= max(0.0, overfit_gap - 0.06) * 0.40
    else:
        fitness = calculate_fitness(validation, train)
        false_negatives = validation.confusion_matrix[1][0]
        fitness -= min(0.08, false_negatives * 0.003)

    return AdvancedIndividual(
        model_family=model_family,
        genes=dict(genes),
        fitness=float(fitness),
        cv_metrics=validation,
    )


def tournament_selection(
    evaluated_population: list[AdvancedIndividual],
    tournament_size: int,
    rng: random.Random,
) -> AdvancedIndividual:
    competitors = rng.sample(evaluated_population, k=min(tournament_size, len(evaluated_population)))
    return max(competitors, key=lambda item: item.fitness)


def crossover(
    parent_a: AdvancedIndividual,
    parent_b: AdvancedIndividual,
    rng: random.Random,
) -> tuple[str, dict[str, Any]]:
    model_family = parent_a.model_family if rng.random() < 0.5 else parent_b.model_family
    source_a = parent_a.genes if parent_a.model_family == model_family else random_individual(rng)[1]
    source_b = parent_b.genes if parent_b.model_family == model_family else random_individual(rng)[1]

    child = {}
    for gene in ADVANCED_GENE_SPACES[model_family]:
        child[gene] = source_a.get(gene) if rng.random() < 0.5 else source_b.get(gene)
        if child[gene] not in ADVANCED_GENE_SPACES[model_family]:
            child[gene] = rng.choice(ADVANCED_GENE_SPACES[model_family][gene])
    return model_family, child


def mutate(
    model_family: str,
    genes: dict[str, Any],
    mutation_rate: float,
    rng: random.Random,
) -> tuple[str, dict[str, Any]]:
    if rng.random() < mutation_rate / 2:
        return random_individual(rng)

    mutated = dict(genes)
    for gene, values in ADVANCED_GENE_SPACES[model_family].items():
        if rng.random() < mutation_rate:
            alternatives = [value for value in values if value != mutated[gene]]
            mutated[gene] = rng.choice(alternatives or values)
    return model_family, mutated


def run_advanced_tuning(
    prepared: PreparedData,
    config: AdvancedTuningConfig | None = None,
    random_state: int = RANDOM_STATE,
) -> AdvancedTuningResult:
    config = config or AdvancedTuningConfig()
    rng = random.Random(random_state + 312)
    population = initial_population(config.population_size, rng)
    cache: dict[str, AdvancedIndividual] = {}
    history: list[dict[str, Any]] = []
    best_overall: AdvancedIndividual | None = None
    generations_without_improvement = 0
    start = time.perf_counter()

    for generation in range(config.generations):
        evaluated = []
        for model_family, genes in population:
            key = chromosome_key(model_family, genes)
            if key not in cache:
                cache[key] = evaluate_cv_individual(
                    prepared,
                    model_family,
                    genes,
                    cv_splits=config.cv_splits,
                    objective=config.objective,
                )
            evaluated.append(cache[key])

        evaluated.sort(key=lambda item: item.fitness, reverse=True)
        best_generation = evaluated[0]
        mean_fitness = sum(item.fitness for item in evaluated) / len(evaluated)
        diversity = len({chromosome_key(item.model_family, item.genes) for item in evaluated})

        if best_overall is None or best_generation.fitness > best_overall.fitness:
            best_overall = best_generation
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1

        history.append(
            {
                "experiment": config.name,
                "generation": generation,
                "best_fitness": best_generation.fitness,
                "mean_fitness": mean_fitness,
                "diversity": diversity,
                "model_family": best_generation.model_family,
                "best_genes": json.dumps(best_generation.genes, sort_keys=True, default=str),
                "recall_pos": best_generation.cv_metrics.recall_pos,
                "f1_pos": best_generation.cv_metrics.f1_pos,
                "auc_roc": best_generation.cv_metrics.auc_roc,
                "accuracy": best_generation.cv_metrics.accuracy,
            }
        )

        if generations_without_improvement >= config.patience:
            break

        elite_count = max(1, int(config.population_size * config.elitism_rate))
        next_population = [
            (item.model_family, dict(item.genes))
            for item in evaluated[:elite_count]
        ]

        while len(next_population) < config.population_size:
            parent_a = tournament_selection(evaluated, config.tournament_size, rng)
            parent_b = tournament_selection(evaluated, config.tournament_size, rng)
            if rng.random() < config.crossover_rate:
                child_family, child_genes = crossover(parent_a, parent_b, rng)
            else:
                child_family, child_genes = parent_a.model_family, dict(parent_a.genes)
            next_population.append(
                mutate(child_family, child_genes, config.mutation_rate, rng)
            )

        population = next_population

    if best_overall is None:
        raise RuntimeError("Tuning avancado terminou sem individuos avaliados.")

    return AdvancedTuningResult(
        config=config,
        best_individual=best_overall,
        history=history,
        elapsed_seconds=time.perf_counter() - start,
    )


def advanced_history_to_frame(result: AdvancedTuningResult) -> pd.DataFrame:
    return pd.DataFrame(result.history)
