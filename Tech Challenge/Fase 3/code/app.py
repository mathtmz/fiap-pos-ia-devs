from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from pcos_fase3.demo_examples import load_demo_diagnosis_example
from pcos_fase3.generation import get_generator_status
from pcos_fase3.graph import run_triage
from pcos_fase3.safety import CLINICIAN_REVIEW_NOTICE

st.set_page_config(page_title="Triagem SOP — acadêmica", layout="wide")
st.title("Assistente acadêmico de apoio à triagem SOP")
st.caption("DEMONSTRAÇÃO ACADÊMICA · Respostas para revisão médica")
st.info(
    "Sem fontes clínicas validadas, o assistente não conclui diagnóstico, prescrição ou dose. "
    "O médico responsável valida e mantém a decisão final."
)

with st.expander(
    "Exemplo didático: hipótese fictícia (não é resposta do assistente)",
    expanded=False,
):
    example = load_demo_diagnosis_example()
    st.caption("Vinheta independente dos registros e do fluxo de triagem")
    st.write(example["case_vignette"])
    st.markdown(f"**{example['mock_output']}**")
    st.warning(example["disclaimer"])
    st.caption(
        "Este cartão é manual e estático. Ele não é gerado pelo modelo nem usado nas consultas."
    )

with st.form("triage_request"):
    patient_id = st.selectbox(
        "Registro para análise",
        ["Nenhum"] + [f"SYN-PCOS-{index:02d}" for index in range(1, 13)],
    )
    question = st.text_area(
        "O que você quer saber?",
        max_chars=800,
        placeholder="Ex.: Resuma os relatos e exames deste registro.",
        help=(
            "Você pode perguntar sobre fontes, relatos, exames, pendências e limites. "
            "Perguntas clínicas individuais dependem de evidência validada e revisão médica."
        ),
    )
    submitted = st.form_submit_button("Consultar", type="primary")

if submitted:
    if not question.strip():
        st.info("Escreva uma pergunta para continuar.")
    else:
        try:
            result = run_triage(
                {
                    "patient_id": None if patient_id == "Nenhum" else patient_id,
                    "question": question,
                }
            )
            response = result["response"].replace(CLINICIAN_REVIEW_NOTICE, "").strip()
            st.subheader("Resposta")
            if result["status"] == "ok":
                st.success("Resposta baseada no material recuperado; revise antes de usar.")
                st.markdown(response)
            elif result["status"] == "blocked":
                st.warning(response)
            elif result["status"] == "abstained":
                st.info(response)
            else:
                st.error(response)

            if result["status"] in {"ok", "abstained"}:
                st.caption(
                    "Rascunho de apoio: o médico responsável avalia e valida o conteúdo, "
                    "mantém a decisão final e medeia qualquer comunicação ao paciente."
                )

            patient = result.get("patient") or {}
            if patient.get("available"):
                record = patient
                with st.expander("Dados do registro consultado", expanded=False):
                    st.json(
                        {
                            "Identificador": record["patient"]["patient_id"],
                            "Faixa etária": record["patient"]["age_band"],
                            "Relatos": record["reported_facts"],
                            "Exames": record["exams"],
                            "Pendências": record["pending"],
                        }
                    )

            sources = result.get("sources", [])
            with st.expander(f"Fontes consultadas ({len(sources)})", expanded=False):
                if sources:
                    for source in sources:
                        title = source["title"]
                        if source.get("source_url"):
                            title = f"[{title}]({source['source_url']})"
                        st.markdown(
                            f"**[{source['source_id']}] {title}** — {source['version']}"
                        )
                        metadata = [source.get("publisher"), source.get("source_type")]
                        if source.get("checked_on"):
                            metadata.append(f"verificada em {source['checked_on']}")
                        if source.get("review_status"):
                            metadata.append(source["review_status"])
                        st.caption(" · ".join(item for item in metadata if item))
                        st.write(source["text"])
                        if source.get("document_url"):
                            st.markdown(f"[Abrir documento integral]({source['document_url']})")
                else:
                    st.write("Nenhuma fonte recuperada.")

            with st.expander("Detalhes técnicos", expanded=False):
                st.caption("Modelo: " + get_generator_status())
                st.code(" → ".join(result["trace"]), language="text")
        except Exception as exc:
            st.error("Não foi possível processar a solicitação. Revise a entrada e tente novamente.")
            with st.expander("Detalhes do erro"):
                st.caption(f"Tipo de erro: {type(exc).__name__}")
