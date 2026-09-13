import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pcos_fase3.graph import run_triage

if __name__ == "__main__":
    print(run_triage({"patient_id": "SYN-PCOS-01", "question": "Quais são os limites da triagem e as pendências simuladas?"}))
