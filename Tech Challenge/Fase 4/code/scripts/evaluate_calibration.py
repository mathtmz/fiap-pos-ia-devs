"""Calibração exploratória em PM_001 e avaliação cega em PM_101."""

import json, sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
sys.path.insert(0, str(CODE / "src"))
from fisio_fase4.video import analyze_video
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

D = ROOT / "data/public"
output = CODE / "outputs/calibracao"
output.mkdir(parents=True, exist_ok=True)


def features(path):
    r = analyze_video(path, output / (path.stem + "_anotado.mp4"), path.stem)
    a = [v["angle"] for v in r["angles"] if v["side"] == "direito"]
    m = [v for v in r["measurements"] if v["side"] == "direito"]
    if len(a) < 3 or len(m) < 3:
        return None
    return {
        "max_angle": max(a),
        "min_elbow_angle": min(v["elbow_angle"] for v in m),
        "max_trunk_tilt": max(v["trunk_tilt"] for v in m),
    }


train = [(D / "rehab_correto.mp4", 0), (D / "rehab_incorreto.mp4", 1)]
test = [(D / "pm101_normal.mp4", 0)] + [
    (D / f"pm101_erro_{i}.mp4", 1) for i in range(1, 6)
]
tr = [(p.name, label, features(p)) for p, label in train]
te = [(p.name, label, features(p)) for p, label in test]
if any(f is None for _, _, f in tr):
    raise SystemExit("Dados de calibração insuficientes")
choices = []
for field, op in [
    ("max_angle", "lt"),
    ("min_elbow_angle", "lt"),
    ("max_trunk_tilt", "gt"),
]:
    cut = (tr[0][2][field] + tr[1][2][field]) / 2
    pred = lambda f: int(f[field] < cut if op == "lt" else f[field] > cut)
    y = [v for _, v, _ in tr]
    yhat = [pred(f) for _, _, f in tr]
    score = precision_recall_fscore_support(y, yhat, average="binary", zero_division=0)[
        2
    ]
    choices.append((score, field, op, cut))
score, field, op, cut = max(choices, key=lambda x: x[0])
valid = [(n, y, f) for n, y, f in te if f is not None]
y = [v for _, v, _ in valid]
predictions = [
    int(f[field] < cut if op == "lt" else f[field] > cut) for _, _, f in valid
]
precision, recall, f1, _ = precision_recall_fscore_support(
    y, predictions, average="binary", zero_division=0
)
result = {
    "train_participant": "PM_001",
    "test_participant": "PM_101",
    "training_count": len(tr),
    "test_count": len(te),
    "test_evaluable": len(valid),
    "field": field,
    "operator": op,
    "threshold": cut,
    "train_f1": score,
    "precision": precision,
    "recall": recall,
    "f1": f1,
    "confusion_matrix_labels_0_1": confusion_matrix(
        y, predictions, labels=[0, 1]
    ).tolist(),
    "test_predictions": [
        {"clip": n, "label": truth, "prediction": pred, "features": f}
        for (n, truth, f), pred in zip(valid, predictions)
    ],
    "limitation": "Calibração com duas repetições de um único participante; não atribui tipo de erro nem valida uso clínico.",
}
(output / "metricas.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False, indent=2))
