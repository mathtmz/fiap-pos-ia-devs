import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from pcos_fase3.graph import run_triage

st.set_page_config(page_title="Triagem SOP — acadêmica", layout="wide")
st.title("Assistente acadêmico de triagem SOP")
st.warning("Demonstração com dados e protocolos fictícios. Não diagnostica, prescreve ou substitui atendimento profissional.")
patient_id = st.selectbox("Paciente sintético", ["Nenhum"] + [f"SYN-PCOS-{i:02d}" for i in range(1, 13)])
question = st.text_area("Pergunta educacional", max_chars=800, placeholder="Ex.: Quais são os limites da triagem?")
if st.button("Executar triagem", type="primary"):
    if not question.strip():
        st.info("Escreva uma pergunta educacional.")
    else:
        try:
            result = run_triage({"patient_id": None if patient_id == "Nenhum" else patient_id, "question": question})
            st.subheader("Resposta validada")
            st.write(result["response"])
            st.caption("Fluxo: " + " → ".join(result["trace"]))
            if result.get("patient"):
                st.subheader("Registro sintético")
                st.json(result["patient"])
            st.subheader("Fontes")
            st.json(result["sources"])
        except Exception:
            st.error("Não foi possível processar a solicitação. Revise a entrada e tente novamente.")
