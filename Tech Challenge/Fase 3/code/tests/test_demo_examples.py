from pcos_fase3.demo_examples import load_demo_diagnosis_example
from pcos_fase3.config import DATA_DIR, DEMO_DIAGNOSIS_FILE
from scripts.create_colab_bundle import bundle_files


def test_demo_diagnosis_is_explicitly_fake_and_isolated():
    example = load_demo_diagnosis_example()
    assert example["fictional"] is True
    assert example["demo_only"] is True
    assert example["not_for_triage"] is True
    assert "hipótese demonstrativa fictícia" in example["mock_output"].casefold()
    assert "manualmente" in example["disclaimer"]
    assert DEMO_DIAGNOSIS_FILE not in bundle_files()
    assert all(path.name != "generate_synthetic_cases.py" for path in bundle_files())
    training_rows = DATA_DIR / "processed" / "instruction"
    assert all(
        "hipótese demonstrativa fictícia" not in path.read_text(encoding="utf-8").casefold()
        for path in training_rows.glob("*.jsonl")
    )
