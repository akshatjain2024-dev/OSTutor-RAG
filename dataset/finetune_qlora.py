import argparse
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

HERE = Path(__file__).resolve().parent


def main(a):
    data = load_dataset("json", data_files={"train": str(HERE / "out/finetune/train.jsonl"),
                                            "validation": str(HERE / "out/finetune/val.jsonl")})
    data = data.remove_columns([c for c in data["train"].column_names if c != "messages"])

    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(
        a.model, device_map="auto", torch_dtype=torch.float16,
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                               bnb_4bit_compute_dtype=torch.float16,
                                               bnb_4bit_use_double_quant=True))

    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                      "gate_proj", "up_proj", "down_proj"])
    cfg = SFTConfig(
        output_dir=str(HERE / "out/lora_runs"), num_train_epochs=a.epochs,
        per_device_train_batch_size=1, gradient_accumulation_steps=8,
        learning_rate=2e-4, lr_scheduler_type="cosine", warmup_ratio=0.05,
        logging_steps=10, eval_strategy="epoch", save_strategy="epoch",
        max_length=a.max_len, fp16=True, gradient_checkpointing=True,
        assistant_only_loss=False, report_to="none")
    trainer = SFTTrainer(model=model, args=cfg, train_dataset=data["train"],
                         eval_dataset=data["validation"], processing_class=tok, peft_config=lora)
    trainer.train()
    trainer.model.save_pretrained(HERE / "out/lora")
    tok.save_pretrained(HERE / "out/lora")
    print("Saved LoRA adapter to", HERE / "out/lora")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--max_len", type=int, default=1536)
    main(ap.parse_args())
