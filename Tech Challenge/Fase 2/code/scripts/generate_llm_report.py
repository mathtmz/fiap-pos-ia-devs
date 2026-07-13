from __future__ import annotations

import sys
from pathlib import Path

import joblib

PROJECT_CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_CODE_DIR / "src"))

from pcos_fase2.config import MODELS_DIR, REPORTS_DIR, ensure_output_dirs
from pcos_fase2.data import prepare_data
from pcos_fase2.explainability import build_patient_explanation_payload, feature_importance_frame
from pcos_fase2.llm_explainer import LLMExplanationRequest, build_prompt, generate_explanation


def main() -> None:
    ensure_output_dirs()
    model_bundle_path = MODELS_DIR / "best_model.joblib"
    if not model_bundle_path.exists():
        raise FileNotFoundError(
            "Modelo otimizado nao encontrado. Execute scripts/run_ga_experiments.py primeiro."
        )

    bundle = joblib.load(model_bundle_path)
    prepared = prepare_data()
    model = bundle["model"]

    importance = feature_importance_frame(model, prepared.feature_names)
    payload = build_patient_explanation_payload(
        model=model,
        patient_index=0,
        x_test=prepared.x_test_scaled,
        y_test=prepared.y_test,
        feature_names=prepared.feature_names,
        global_importance=importance,
    )

    request = LLMExplanationRequest(
        model_name="Random Forest otimizado por algoritmo genetico",
        probability_pcos=payload["probability_pcos"],
        predicted_label=payload["predicted_label"],
        top_features=payload["top_global_features"],
        model_metrics=bundle["metrics"],
    )
    prompt = build_prompt(request)
    response, safety = generate_explanation(request)

    report = f"""# Explicacao com LLM - Exemplo de Paciente

## Prompt usado

```text
{prompt}
```

## Resposta gerada

{response}

## Checagem de seguranca

{safety}
"""
    output_path = REPORTS_DIR / "llm_explanation.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"Relatorio LLM salvo em: {output_path}")


if __name__ == "__main__":
    main()
