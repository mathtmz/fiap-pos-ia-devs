import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pcos_fase3.generation import get_generator_status
from pcos_fase3.graph import run_triage

if __name__ == "__main__":
    result = run_triage(
        {
            "patient_id": "SYN-PCOS-01",
            "question": "Quais são os limites da triagem e as pendências registradas?",
        }
    )
    print("MODELO:", get_generator_status())
    if result.get("patient", {}).get("available"):
        patient = result["patient"]["patient"]
        patient.pop("synthetic_notice", None)
    print("AMBIENTE DE SIMULAÇÃO ACADÊMICA")
    print(result)
