from pcos_fase2.advanced_tuning import (
    ADVANCED_GENE_SPACES,
    build_tuned_model,
    strip_search_only_genes,
)


def test_strip_search_only_genes_removes_threshold():
    genes = {
        "n_estimators": 100,
        "max_depth": 8,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "max_features": "sqrt",
        "class_weight": "balanced",
        "threshold": 0.40,
    }

    model_genes, threshold = strip_search_only_genes(genes)

    assert threshold == 0.40
    assert "threshold" not in model_genes


def test_build_tuned_model_accepts_advanced_random_forest_genes():
    genes = {
        gene: values[0]
        for gene, values in ADVANCED_GENE_SPACES["random_forest"].items()
    }

    model = build_tuned_model("random_forest", genes)

    assert model.__class__.__name__ == "RandomForestClassifier"
