from __future__ import annotations

import pandas as pd
from sklearn.inspection import permutation_importance

from .config import GENERATED_FEATURES, RANDOM_STATE


def feature_importance_frame(model, feature_names: list[str]) -> pd.DataFrame:
    if not hasattr(model, "feature_importances_"):
        raise ValueError("O modelo informado nao possui feature_importances_.")

    frame = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": model.feature_importances_,
            "type": [
                "feature_engineering" if feature in GENERATED_FEATURES else "original"
                for feature in feature_names
            ],
        }
    )
    return frame.sort_values("importance", ascending=False).reset_index(drop=True)


def permutation_importance_frame(model, x_test, y_test, feature_names: list[str]) -> pd.DataFrame:
    result = permutation_importance(
        model,
        x_test,
        y_test,
        n_repeats=10,
        random_state=RANDOM_STATE,
        scoring="f1",
    )
    frame = pd.DataFrame(
        {
            "feature": feature_names,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    )
    return frame.sort_values("importance_mean", ascending=False).reset_index(drop=True)


def build_patient_explanation_payload(
    model,
    patient_index: int,
    x_test,
    y_test,
    feature_names: list[str],
    global_importance: pd.DataFrame,
) -> dict:
    probabilities = model.predict_proba(x_test[[patient_index]])[0]
    prediction = int(model.predict(x_test[[patient_index]])[0])
    top_features = global_importance.head(5)["feature"].tolist()

    return {
        "patient_index": patient_index,
        "real_label": int(y_test.iloc[patient_index]),
        "predicted_label": prediction,
        "probability_pcos": float(probabilities[1]),
        "top_global_features": top_features,
        "feature_names_available": feature_names,
    }
