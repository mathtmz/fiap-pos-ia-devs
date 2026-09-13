"""Optional local/Colab LoRA training. It is intentionally not run by the demo or tests."""
import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrainingConfig:
    model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"
    epochs: int = 2
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    use_qlora: bool = False


def format_example(example: dict) -> str:
    return "\n".join(f"{message['role'].upper()}: {message['content']}" for message in example["messages"])


def train(config: TrainingConfig, data_dir: Path, output_dir: Path) -> None:
    """Train adapters only; no patient record, key or external API is involved."""
    from datasets import load_dataset
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import (AutoModelForCausalLM, AutoTokenizer, DataCollatorForLanguageModeling,
                              Trainer, TrainingArguments)

    quantization_config = None
    if config.use_qlora:
        from transformers import BitsAndBytesConfig
        import torch
        quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    tokenizer = AutoTokenizer.from_pretrained(config.model_name, trust_remote_code=False)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(config.model_name, trust_remote_code=False, quantization_config=quantization_config)
    model.config.use_cache = False
    adapter = LoraConfig(task_type=TaskType.CAUSAL_LM, r=8, lora_alpha=16, lora_dropout=0.05, target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
    model = get_peft_model(model, adapter)
    dataset = load_dataset("json", data_files={"train": str(data_dir / "train.jsonl"), "validation": str(data_dir / "validation.jsonl")})

    def tokenize(batch: dict) -> dict:
        return tokenizer([format_example(row) for row in batch["messages"]], truncation=True, max_length=1024)

    tokenized = dataset.map(tokenize, batched=True, remove_columns=dataset["train"].column_names)
    arguments = TrainingArguments(output_dir=str(output_dir), num_train_epochs=config.epochs, per_device_train_batch_size=config.per_device_train_batch_size,
                                 gradient_accumulation_steps=config.gradient_accumulation_steps, eval_strategy="epoch", save_strategy="epoch", logging_steps=10,
                                 report_to=[], remove_unused_columns=False)
    trainer = Trainer(model=model, args=arguments, train_dataset=tokenized["train"], eval_dataset=tokenized["validation"],
                      data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False))
    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qlora", action="store_true", help="Usa quantização 4-bit; requer GPU compatível.")
    parser.add_argument("--run", action="store_true", help="Inicia o treino; sem esta flag apenas valida a configuração.")
    args = parser.parse_args()
    config = TrainingConfig(use_qlora=args.qlora)
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "data" / "processed" / "instruction"
    output_dir = root / "code" / "outputs" / "lora_adapter"
    if args.run:
        train(config, data_dir, output_dir)
    else:
        print("Configuração LoRA pronta; use --run em GPU/Colab após gerar os dados:", config)
    print("Fine-tuning ajusta formato e limites; RAG permanece responsável por fatos e protocolos atualizáveis.")


if __name__ == "__main__":
    main()
