import random

from pcos_fase2.evaluation import ModelMetrics, calculate_fitness
from pcos_fase2.genetic_optimizer import (
    GENE_SPACES,
    crossover,
    initial_population,
    mutate,
    random_chromosome,
)


def test_random_chromosome_respects_gene_space():
    rng = random.Random(42)
    chromosome = random_chromosome("random_forest", rng)

    for gene, value in chromosome.items():
        assert value in GENE_SPACES["random_forest"][gene]


def test_initial_population_includes_valid_individuals():
    rng = random.Random(42)
    population = initial_population("random_forest", population_size=10, rng=rng)

    assert len(population) == 10
    for chromosome in population:
        for gene, value in chromosome.items():
            assert value in GENE_SPACES["random_forest"][gene]


def test_crossover_and_mutation_keep_valid_genes():
    rng = random.Random(42)
    parent_a = random_chromosome("random_forest", rng)
    parent_b = random_chromosome("random_forest", rng)

    child = crossover(parent_a, parent_b, "random_forest", rng)
    mutated = mutate(child, "random_forest", mutation_rate=1.0, rng=rng)

    for gene, value in mutated.items():
        assert value in GENE_SPACES["random_forest"][gene]


def test_fitness_prioritizes_better_validation_metrics():
    weak = ModelMetrics(0.70, 0.65, 0.60, 0.62, 0.75, [[50, 10], [12, 18]])
    strong = ModelMetrics(0.90, 0.88, 0.92, 0.90, 0.95, [[70, 3], [2, 34]])

    assert calculate_fitness(strong) > calculate_fitness(weak)
