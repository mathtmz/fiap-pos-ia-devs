"""Creates exactly 600 synthetic instruction examples; no clinical record is used."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed" / "instruction"
SPLITS = {"train": 420, "validation": 90, "test": 90}
TOPICS = ["limites da triagem", "fontes e rastreabilidade", "pendências simuladas", "abstinência por falta de evidência", "proteção de dados"]


def record(index: int, split: str) -> dict:
    topic = TOPICS[index % len(TOPICS)]
    question = f"Explique {topic} no assistente acadêmico de SOP."
    answer = ("Resposta educacional: o sistema usa apenas contexto rastreável e dados sintéticos. "
              "Não confirma diagnóstico, não prescreve e exige validação de profissional habilitado. "
              "Quando não houver fonte suficiente, deve se abster.")
    return {"messages": [{"role": "system", "content": "Você é um assistente acadêmico seguro de SOP."}, {"role": "user", "content": question}, {"role": "assistant", "content": answer}], "metadata": {"synthetic": True, "split": split, "id": f"SYN-INS-{index:03d}"}}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    offset = 0
    for split, count in SPLITS.items():
        rows = [record(offset + index, split) for index in range(count)]
        offset += count
        (OUT / f"{split}.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text("600 exemplos sintéticos: 420 treino, 90 validação, 90 teste. Uso: formato, tom, limites e recusa; nunca fatos clínicos mutáveis.\n", encoding="utf-8")
    print("Dados instrucionais sintéticos criados.")


if __name__ == "__main__":
    main()
