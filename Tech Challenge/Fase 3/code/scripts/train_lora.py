"""Train and evaluate a LoRA/QLoRA adapter using only synthetic instructions."""
import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_ROOT / "src"))
from pcos_fase3.config import MODEL_NAME


@dataclass(frozen=True)
class TrainingConfig:
    model_name: str = MODEL_NAME
    epochs: int = 2
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    max_length: int = 1024
    use_qlora: bool = False


def format_example(example: dict) -> str:
    return "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in example["messages"]
    )


def tokenize_example(example: dict, tokenizer, max_length: int = 1024) -> dict:
    """Use the model chat template and mask system/user tokens from the loss."""
    messages = example["messages"]
    if not messages or messages[-1]["role"] != "assistant":
        raise ValueError("Cada exemplo precisa terminar com uma resposta de assistant.")
    prompt_messages = messages[:-1]
    if hasattr(tokenizer, "apply_chat_template"):
        full_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        prompt_text = tokenizer.apply_chat_template(
            prompt_messages, tokenize=False, add_generation_prompt=True
        )
    else:
        full_text = format_example(example)
        prompt_text = format_example({"messages": prompt_messages}) + "\nASSISTANT:"

    input_ids = tokenizer(
        full_text, add_special_tokens=False, truncation=True, max_length=max_length
    )["input_ids"]
    prompt_ids = tokenizer(
        prompt_text, add_special_tokens=False, truncation=True, max_length=max_length
    )["input_ids"]
    prompt_length = min(len(prompt_ids), len(input_ids))
    if input_ids[:prompt_length] != prompt_ids[:prompt_length]:
        raise ValueError("O template do modelo não preservou o prefixo de prompt esperado.")
    labels = [-100] * prompt_length + input_ids[prompt_length:]
    if not any(label != -100 for label in labels):
        raise ValueError("O exemplo foi truncado antes do conteúdo da resposta.")
    return {"input_ids": input_ids, "attention_mask": [1] * len(input_ids), "labels": labels}


def _json_safe(value):
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return _json_safe(value.item())
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        return None
    return value


def train(config: TrainingConfig, data_dir: Path, output_dir: Path) -> dict:
    import torch
    from datasets import load_dataset
    from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        DataCollatorForSeq2Seq,
        Trainer,
        TrainingArguments,
    )

    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    required = [data_dir / f"{split}.jsonl" for split in ("train", "validation", "test")]
    missing = [path.name for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Faltam divisões de dados instrucionais: {', '.join(missing)}")
    if config.use_qlora and not torch.cuda.is_available():
        raise RuntimeError("QLoRA requer uma GPU CUDA; execute em ambiente Colab com GPU.")

    output_dir.mkdir(parents=True, exist_ok=True)
    compute_dtype = (
        torch.bfloat16
        if torch.cuda.is_available() and torch.cuda.is_bf16_supported()
        else torch.float16
    )
    quantization_config = None
    if config.use_qlora:
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=True,
        )

    tokenizer = AutoTokenizer.from_pretrained(
        config.model_name, trust_remote_code=False
    )
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    model_kwargs = {"trust_remote_code": False}
    if quantization_config is not None:
        model_kwargs["quantization_config"] = quantization_config
    if torch.cuda.is_available():
        model_kwargs["device_map"] = {"": torch.cuda.current_device()}
        model_kwargs["dtype"] = compute_dtype
    model = AutoModelForCausalLM.from_pretrained(config.model_name, **model_kwargs)
    model.config.use_cache = False
    if config.use_qlora:
        model = prepare_model_for_kbit_training(model)
    model.gradient_checkpointing_enable()

    adapter = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    model = get_peft_model(model, adapter)
    model.print_trainable_parameters()

    dataset = load_dataset(
        "json",
        data_files={
            split: str(data_dir / f"{split}.jsonl")
            for split in ("train", "validation", "test")
        },
    )
    tokenized = dataset.map(
        tokenize_example,
        fn_kwargs={"tokenizer": tokenizer, "max_length": config.max_length},
        remove_columns=dataset["train"].column_names,
    )
    supports_bf16 = bool(torch.cuda.is_available() and torch.cuda.is_bf16_supported())
    arguments = TrainingArguments(
        output_dir=str(output_dir / "checkpoints"),
        num_train_epochs=config.epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        logging_steps=10,
        report_to=[],
        remove_unused_columns=False,
        gradient_checkpointing=True,
        fp16=bool(torch.cuda.is_available() and not supports_bf16),
        bf16=supports_bf16,
    )
    trainer = Trainer(
        model=model,
        args=arguments,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        data_collator=DataCollatorForSeq2Seq(
            tokenizer=tokenizer, model=model, label_pad_token_id=-100, pad_to_multiple_of=8
        ),
    )
    train_result = trainer.train()
    validation_metrics = trainer.evaluate(
        eval_dataset=tokenized["validation"], metric_key_prefix="validation"
    )
    test_metrics = trainer.evaluate(
        eval_dataset=tokenized["test"], metric_key_prefix="test"
    )
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "synthetic_data_only": True,
        "model_name": config.model_name,
        "config": asdict(config),
        "dataset_sizes": {split: len(dataset[split]) for split in dataset},
        "train_metrics": _json_safe(train_result.metrics),
        "validation_metrics": _json_safe(validation_metrics),
        "test_metrics": _json_safe(test_metrics),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "note": "Losses são métricas de engenharia do conjunto sintético, não validação clínica.",
    }
    (output_dir / "training_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qlora", action="store_true", help="Usa quantização 4-bit em GPU CUDA.")
    parser.add_argument("--run", action="store_true", help="Inicia o treinamento.")
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--model-name", default=MODEL_NAME)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--max-length", type=int, default=1024)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    data_dir = args.data_dir or root / "data" / "processed" / "instruction"
    output_dir = args.output_dir or root / "code" / "outputs" / "lora_adapter"
    config = TrainingConfig(
        model_name=args.model_name,
        epochs=args.epochs,
        max_length=args.max_length,
        use_qlora=args.qlora,
    )
    if not args.run:
        print("Configuração validada. Para treinar no Colab, use: --run --qlora")
        print(config)
        return
    summary = train(config, data_dir, output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
