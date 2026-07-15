import mlflow

from pcos_fase2.experiment_tracking import log_run_to_mlflow


def test_log_run_to_mlflow_writes_params_and_metrics(tmp_path):
    tracking_dir = tmp_path / "mlruns"
    artifact = tmp_path / "history.jsonl"
    artifact.write_text('{"generation": 0}\n', encoding="utf-8")

    log_run_to_mlflow(
        experiment_name="teste_ga",
        run_name="job_teste",
        params={"population_size": 10, "mutation_rate": 0.1},
        metrics={"best_fitness": 0.9, "confusion_matrix": [[1, 0], [0, 1]]},
        artifact_paths=[artifact],
        tracking_dir=tracking_dir,
    )

    mlflow.set_tracking_uri(f"file:{tracking_dir}")
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("teste_ga")

    assert experiment is not None

    runs = client.search_runs(experiment_ids=[experiment.experiment_id])
    assert len(runs) == 1

    run = runs[0]
    assert run.data.params["population_size"] == "10"
    assert run.data.metrics["best_fitness"] == 0.9
    assert "confusion_matrix" not in run.data.metrics

    artifacts = client.list_artifacts(run.info.run_id)
    assert any(item.path == "history.jsonl" for item in artifacts)


def test_log_run_to_mlflow_skips_missing_artifacts(tmp_path):
    tracking_dir = tmp_path / "mlruns"
    missing_artifact = tmp_path / "nao_existe.jsonl"

    log_run_to_mlflow(
        experiment_name="teste_ga_sem_artefato",
        run_name="job_sem_artefato",
        params={"population_size": 5},
        metrics={"best_fitness": 0.5},
        artifact_paths=[missing_artifact],
        tracking_dir=tracking_dir,
    )

    mlflow.set_tracking_uri(f"file:{tracking_dir}")
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("teste_ga_sem_artefato")

    assert experiment is not None
