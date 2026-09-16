from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
SYNTHETIC_DB = DATA_DIR / "synthetic" / "pcos_synthetic.sqlite"
CASE_PROFILES_FILE = DATA_DIR / "synthetic" / "case_profiles.jsonl"
DEMO_DIAGNOSIS_FILE = DATA_DIR / "synthetic" / "demo_diagnosis.json"
CORPUS_FILE = DATA_DIR / "processed" / "corpus.jsonl"
AUDIT_FILE = PROJECT_ROOT / "code" / "outputs" / "audit.jsonl"
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
MODEL_ADAPTER_DIR = PROJECT_ROOT / "code" / "outputs" / "lora_adapter"
MAX_QUESTION_LENGTH = 800
RETRIEVAL_K = 3
