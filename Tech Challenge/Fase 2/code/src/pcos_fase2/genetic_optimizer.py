from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.model_selection import train_test_split

from .config import RANDOM_STATE
from .data import PreparedData
from .evaluation import ModelMetrics, calculate_fitness, evaluate_classifier
from .models import build_model_from_chromosome


GENE_SPACES: dict[str, dict[str, list[Any]]] = {
    "random_forest": {
        "n_estimators": [50, 100, 150, 200, 300, 500],
        "max_depth": [None, 3, 5, 8, 12, 16, 24, 32],
        "min_samples_split": [2, 4, 6, 8, 10, 15, 20],
        "min_samples_leaf": [1, 2, 3, 4, 5, 8, 10],
        "max_features": ["sqrt", "log2", None],
        "class_weight": ["balanced", "balanced_subsample", None],
    },
    "logistic_regression": {
        "C": [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
        "penalty": ["l1", "l2"],
        "solver": ["liblinear", "saga"],
        "class_weight": ["balanced", None],
        "max_iter": [500, 1000, 2000, 3000],
    },
}


HOTSTARTS: dict[str, list[dict[str, Any]]] = {
    "random_forest": [
        {
            "n_estimators": 100,
            "max_depth": 12,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "max_features": "sqrt",
            "class_weight": "balanced",
        }
    ],
    "logistic_regression": [
        {
            "C": 1.0,
            "penalty": "l2",
            "solver": "liblinear",
            "class_weight": "balanced",
            "max_iter": 1000,
        }
    ],
}


@dataclass(frozen=True)
class GeneticExperimentConfig:
    name: str
    population_size: int
    generations: int
    mutation_rate: float
    crossover_rate: float
    elitism_rate: float = 0.10
    tournament_size: int = 3
    patience: int = 8


@dataclass
class EvaluatedIndividual:
    genes: dict[str, Any]
    fitness: float
    validation_metrics: ModelMetrics
    train_metrics: ModelMetrics


@dataclass
class GeneticExperimentResult:
    config: GeneticExperimentConfig
    model_family: str
    best_individual: EvaluatedIndividual
    history: list[dict[str, Any]]
    elapsed_seconds: float


def chromosome_key(genes: dict[str, Any]) -> str:
    return json.dumps(genes, sort_keys=True, default=str)


def random_chromosome(model_family: str, rng: random.Random) -> dict[str, Any]:
    return {gene: rng.choice(values) for gene, values in GENE_SPACES[model_family].items()}


def initial_population(
    model_family: str, population_size: int, rng: random.Random
) -> list[dict[str, Any]]:
    population = [dict(item) for item in HOTSTARTS.get(model_family, [])]
    while len(population) < population_size:
        population.append(random_chromosome(model_family, rng))
    return population[:population_size]


def crossover(
    parent_a: dict[str, Any],
    parent_b: dict[str, Any],
    model_family: str,
    rng: random.Random,
) -> dict[str, Any]:
    child = {}
    for gene in GENE_SPACES[model_family]:
        child[gene] = parent_a[gene] if rng.random() < 0.5 else parent_b[gene]
    return child


def mutate(
    genes: dict[str, Any],
    model_family: str,
    mutation_rate: float,
    rng: random.Random,
) -> dict[str, Any]:
    mutated = dict(genes)
    for gene, values in GENE_SPACES[model_family].items():
        if rng.random() < mutation_rate:
            current = mutated[gene]
            alternatives = [value for value in values if value != current]
            mutated[gene] = rng.choice(alternatives or values)
    return mutated


def tournament_selection(
    evaluated_population: list[EvaluatedIndividual],
    tournament_size: int,
    rng: random.Random,
) -> EvaluatedIndividual:
    competitors = rng.sample(evaluated_population, k=min(tournament_size, len(evaluated_population)))
    return max(competitors, key=lambda item: item.fitness)


def make_validation_split(prepared: PreparedData, random_state: int = RANDOM_STATE):
    return train_test_split(
        prepared.x_train_scaled,
        prepared.y_train,
        test_size=0.25,
        stratify=prepared.y_train,
        random_state=random_state,
    )


def evaluate_individual(
    model_family: str,
    genes: dict[str, Any],
    train_x,
    valid_x,
    train_y,
    valid_y,
) -> EvaluatedIndividual:
    model = build_model_from_chromosome(model_family, genes)
    model.fit(train_x, train_y)

    validation_metrics = evaluate_classifier(model, valid_x, valid_y)
    train_metrics = evaluate_classifier(model, train_x, train_y)
    fitness = calculate_fitness(validation_metrics, train_metrics)

    return EvaluatedIndividual(
        genes=dict(genes),
        fitness=fitness,
        validation_metrics=validation_metrics,
        train_metrics=train_metrics,
    )


def run_genetic_experiment(
    prepared: PreparedData,
    model_family: str,
    config: GeneticExperimentConfig,
    log_path: Path | None = None,
    random_state: int = RANDOM_STATE,
) -> GeneticExperimentResult:
    rng = random.Random(random_state + abs(hash((config.name, model_family))) % 10000)
    train_x, valid_x, train_y, valid_y = make_validation_split(prepared, random_state)

    population = initial_population(model_family, config.population_size, rng)
    cache: dict[str, EvaluatedIndividual] = {}
    history: list[dict[str, Any]] = []
    best_overall: EvaluatedIndividual | None = None
    generations_without_improvement = 0
    start = time.perf_counter()

    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("", encoding="utf-8")

    for generation in range(config.generations):
        evaluated_population = []
        for genes in population:
            key = chromosome_key(genes)
            if key not in cache:
                cache[key] = evaluate_individual(
                    model_family, genes, train_x, valid_x, train_y, valid_y
                )
            evaluated_population.append(cache[key])

        evaluated_population.sort(key=lambda item: item.fitness, reverse=True)
        best_generation = evaluated_population[0]
        mean_fitness = sum(item.fitness for item in evaluated_population) / len(evaluated_population)
        diversity = len({chromosome_key(item.genes) for item in evaluated_population})

        if best_overall is None or best_generation.fitness > best_overall.fitness:
            best_overall = best_generation
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1

        history_item = {
            "experiment": config.name,
            "model_family": model_family,
            "generation": generation,
            "best_fitness": best_generation.fitness,
            "mean_fitness": mean_fitness,
            "diversity": diversity,
            "best_genes": json.dumps(best_generation.genes, sort_keys=True, default=str),
            "recall_pos": best_generation.validation_metrics.recall_pos,
            "f1_pos": best_generation.validation_metrics.f1_pos,
            "auc_roc": best_generation.validation_metrics.auc_roc,
            "accuracy": best_generation.validation_metrics.accuracy,
        }
        history.append(history_item)

        if log_path:
            with log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(json.dumps(history_item, ensure_ascii=False) + "\n")

        if generations_without_improvement >= config.patience:
            break

        elite_count = max(1, int(config.population_size * config.elitism_rate))
        next_population = [dict(item.genes) for item in evaluated_population[:elite_count]]

        while len(next_population) < config.population_size:
            parent_a = tournament_selection(evaluated_population, config.tournament_size, rng)
            parent_b = tournament_selection(evaluated_population, config.tournament_size, rng)
            if rng.random() < config.crossover_rate:
                child = crossover(parent_a.genes, parent_b.genes, model_family, rng)
            else:
                child = dict(parent_a.genes)
            next_population.append(mutate(child, model_family, config.mutation_rate, rng))

        population = next_population

    if best_overall is None:
        raise RuntimeError("Experimento genetico terminou sem individuos avaliados.")

    return GeneticExperimentResult(
        config=config,
        model_family=model_family,
        best_individual=best_overall,
        history=history,
        elapsed_seconds=time.perf_counter() - start,
    )


def history_to_frame(results: list[GeneticExperimentResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.extend(result.history)
    return pd.DataFrame(rows)
