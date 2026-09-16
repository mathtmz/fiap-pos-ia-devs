import json
from pathlib import Path

from scripts.train_lora import tokenize_example

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CharacterTokenizer:
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        rendered = "".join(
            f"<{message['role']}>{message['content']}</{message['role']}>"
            for message in messages
        )
        if add_generation_prompt:
            rendered += "<assistant>"
        return rendered

    def __call__(self, text, add_special_tokens=False, truncation=True, max_length=1024):
        return {"input_ids": [ord(character) for character in text[:max_length]]}


def test_instruction_splits_are_diverse_and_disjoint():
    rows = []
    for split in ("train", "validation", "test"):
        path = PROJECT_ROOT / "data" / "processed" / "instruction" / f"{split}.jsonl"
        rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())
    questions = [row["messages"][-2]["content"] for row in rows]
    assert len(rows) == 600
    assert len(set(questions)) == 600
    assert {row["metadata"]["split"] for row in rows} == {"train", "validation", "test"}
    assert all(row["metadata"]["synthetic"] for row in rows)


def test_training_masks_prompt_tokens_and_trains_assistant_response():
    example = {
        "messages": [
            {"role": "system", "content": "Use apenas fontes sintéticas."},
            {"role": "user", "content": "Quais são os limites?"},
            {"role": "assistant", "content": "Não diagnostica nem prescreve."},
        ]
    }
    encoded = tokenize_example(example, CharacterTokenizer())
    first_train_label = next(index for index, label in enumerate(encoded["labels"]) if label != -100)
    assert first_train_label > 0
    assert all(label == -100 for label in encoded["labels"][:first_train_label])
    assert encoded["labels"][first_train_label:] == encoded["input_ids"][first_train_label:]
