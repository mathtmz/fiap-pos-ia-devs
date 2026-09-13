from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
SYNTHETIC_DB = DATA_DIR / "synthetic" / "pcos_synthetic.sqlite"
CORPUS_FILE = DATA_DIR / "processed" / "corpus.jsonl"
AUDIT_FILE = PROJECT_ROOT / "code" / "outputs" / "audit.jsonl"
MAX_QUESTION_LENGTH = 800
RETRIEVAL_K = 3
