"""Safety-first triage workflow shared by the offline demo and LangGraph."""
from __future__ import annotations

import time
import re
from typing import Callable, TypedDict

from .audit import log_event, new_run_id
from .models import TriageRequest
from .patient_store import patient_summary
from .retrieval import retrieve
from .safety import (
    add_clinician_notice,
    is_individual_clinical_request,
    safety_decision,
    validate_answer,
)

Generator = Callable[[dict], str]
RECORD_QUESTION = re.compile(
    r"\b(registro|prontuário|prontuario|paciente|sintomas?|queixas?|exames?|pendências?|pendencias?|"
    r"histórico|historico|resuma|resumo|caso|informações do caso|informacoes do caso)\b",
    re.IGNORECASE,
)


def _record_source(patient: dict) -> dict:
    record = patient["patient"]
    facts = patient.get("reported_facts", [])
    exams = patient.get("exams", [])
    pending = patient.get("pending", [])
    fact_text = "; ".join(
        f"{item['category']}: {item['detail']}" for item in facts
    ) or "Nenhum relato registrado."
    exam_text = "; ".join(
        f"{item['exam_name']}: {item['status']} — {item['summary']}" for item in exams
    ) or "Nenhum exame registrado."
    pending_text = ", ".join(pending) if pending else "nenhuma pendência registrada"
    return {
        "source_id": "DB-RECORD-001",
        "title": f"Registro de demonstração {record['patient_id']}",
        "version": "demo-1",
        "clinical_validated": False,
        "kind": "patient_record",
        "text": (
            f"Identificador {record['patient_id']}; faixa etária registrada {record['age_band']}. "
            f"Relatos anotados, sem interpretação: {fact_text}. "
            f"Exames e status registrados: {exam_text}. Pendências: {pending_text}. "
            "Esses campos reproduzem o registro e não representam conclusão diagnóstica."
        ),
    }


class TriageState(TypedDict, total=False):
    request: TriageRequest
    run_id: str
    started_at: float
    trace: list[str]
    patient: dict
    sources: list[dict]
    response: str
    status: str
    audit_decision: str


def _deterministic_answer(state: TriageState) -> str:
    """Concise offline answer grounded in one or two relevant sources."""
    sources = state["sources"]
    question = state["request"].question.casefold()
    if is_individual_clinical_request(state["request"].question):
        citations = " ".join(f"[{source['source_id']}]" for source in sources)
        return (
            "**Solicitação recebida**\n\n"
            "As fontes disponíveis não têm validação clínica suficiente para sustentar "
            "uma conclusão individual.\n\n"
            "**Próximo passo**\n\n"
            "O médico responsável deve avaliar o caso e tomar a decisão final.\n\n"
            f"**Fontes consultadas:** {citations}"
        )
    capability_question = any(
        phrase in question
        for phrase in (
            "o que você pode responder",
            "o que voce pode responder",
            "quais perguntas posso fazer",
            "como você pode ajudar",
            "como voce pode ajudar",
            "capacidades do assistente",
        )
    )
    if capability_question:
        faq = next((source for source in sources if "faq" in source["title"].casefold()), sources[0])
        faq_id = faq["source_id"]
        return (
            "**Posso ajudar com**\n\n"
            "- Explicar o que dizem as fontes recuperadas.\n"
            "- Resumir relatos, exames e pendências de um registro selecionado.\n\n"
            "**Limite atual**\n\n"
            "Com as fontes disponíveis, não concluo diagnóstico, prescrição ou dose "
            "individual. Essa decisão cabe ao médico responsável.\n\n"
            f"**Fonte:** [{faq_id}]"
        )

    record_source = next(
        (source for source in sources if source.get("kind") == "patient_record"),
        None,
    )
    if record_source:
        patient = state.get("patient", {})
        record = patient.get("patient", {})
        lines = ["**Resumo do registro**"]
        if record.get("age_band"):
            lines.extend(["", f"- Faixa etária: {record['age_band']}."])
        facts = patient.get("reported_facts", [])
        if facts:
            lines.extend(["", "**Relatos registrados**"])
            lines.extend(f"- {fact['category']}: {fact['detail']}" for fact in facts)
        exams = patient.get("exams", [])
        if exams:
            lines.extend(["", "**Exames**"])
            lines.extend(
                f"- {exam['exam_name']}: {exam['status']}." for exam in exams
            )
        pending = patient.get("pending", [])
        if pending:
            lines.extend(["", "**Pendências**"])
            lines.extend(f"- {item}." for item in pending)
        else:
            lines.extend(["", "**Pendências:** nenhuma registrada."])
        lines.extend(
            [
                "",
                "Os relatos e status são reproduzidos como estão no registro; não são uma conclusão diagnóstica.",
                f"\n**Fonte:** [{record_source['source_id']}]",
            ]
        )
        return "\n".join(lines)

    source = sources[0]
    excerpt = source["text"].strip()
    if len(excerpt) > 280:
        excerpt = excerpt[:277].rsplit(" ", 1)[0] + "…"
    return f"**{source['title']}**\n\n{excerpt}\n\n**Fonte:** [{source['source_id']}]"


def _initial_state(request: TriageRequest) -> TriageState:
    return {
        "request": request,
        "run_id": new_run_id(),
        "started_at": time.perf_counter(),
        "trace": [],
    }


def run_triage(payload: dict | TriageRequest, generator: Generator | None = None) -> dict:
    """Validate and run one request through the same graph used by the application."""
    request = (
        payload
        if isinstance(payload, TriageRequest)
        else TriageRequest.model_validate(payload)
    )
    result = build_langgraph(generator=generator).invoke(_initial_state(request))
    return {
        "status": result.get("status", "error"),
        "response": result.get("response", "Não foi possível processar a solicitação."),
        "sources": result.get("sources", []),
        "trace": result.get("trace", []),
        "run_id": result["run_id"],
        "patient": result.get("patient"),
    }


def build_langgraph(generator: Generator | None = None):
    """Build the safety, patient lookup, retrieval, generation and audit graph.

    A supplied generator is useful for deterministic tests. Otherwise the local
    LoRA adapter is loaded lazily on the first eligible generation request; when
    it is not installed, the demo uses the deterministic fallback.
    """
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:  # pragma: no cover - dependency-specific path
        raise RuntimeError("Instale langgraph para materializar o grafo visual.") from exc

    def validate_input(state: TriageState) -> dict:
        request = state["request"]
        decision = safety_decision(request.question)
        trace = state.get("trace", []) + ["validate_input"]
        if decision:
            return {
                "status": "blocked",
                "response": decision,
                "audit_decision": "safety_refusal",
                "trace": trace,
            }
        return {"status": "ok", "trace": trace}

    def consult_record(state: TriageState) -> dict:
        patient = patient_summary(state["request"].patient_id)
        return {
            "patient": patient,
            "trace": state["trace"] + ["consult_record"],
        }

    def retrieve_evidence(state: TriageState) -> dict:
        sources = retrieve(state["request"].question)
        patient = state.get("patient", {})
        if (
            patient.get("available")
            and RECORD_QUESTION.search(state["request"].question)
        ):
            sources = [_record_source(patient), *sources]
        return {
            "sources": sources,
            "trace": state["trace"] + ["retrieve_evidence"],
        }

    def assess_evidence(state: TriageState) -> dict:
        if not state.get("sources"):
            return {
                "status": "abstained",
                "response": add_clinician_notice(
                    "Não há evidência suficiente no corpus local para responder com "
                    "segurança. Consulte fontes revisadas e o médico responsável."
                ),
                "audit_decision": "insufficient_evidence",
                "trace": state["trace"] + ["assess_evidence", "abstain"],
            }
        return {
            "status": "ok",
            "trace": state["trace"] + ["assess_evidence"],
        }

    def generate_answer(state: TriageState) -> dict:
        trace = state["trace"] + ["generate_contextualized_response"]
        try:
            selected_generator = generator
            if selected_generator is None:
                from .generation import get_default_generator

                selected_generator = get_default_generator()
            if selected_generator is None:
                response = _deterministic_answer(state)
            else:
                response = selected_generator(
                    {
                        "question": state["request"].question,
                        "patient": state.get("patient"),
                        "sources": state["sources"],
                    }
                )
                if not isinstance(response, str) or not response.strip():
                    raise ValueError("O modelo retornou uma resposta vazia.")
                response = response.strip()
            return {"response": add_clinician_notice(response), "trace": trace}
        except Exception:
            return {
                "status": "error",
                "response": add_clinician_notice(
                    "Não foi possível gerar o rascunho de apoio. Tente novamente "
                    "ou consulte o médico responsável."
                ),
                "audit_decision": "generation_error",
                "trace": trace,
            }

    def validate_generated_answer(state: TriageState) -> dict:
        if state.get("status") == "error":
            return {"trace": state["trace"] + ["validate_safety_and_citations"]}
        failure = validate_answer(state["response"], state["sources"])
        if failure:
            if failure.startswith("A resposta não contém citação rastreável."):
                fallback = add_clinician_notice(_deterministic_answer(state))
                if validate_answer(fallback, state["sources"]) is None:
                    return {
                        "status": "ok",
                        "response": fallback,
                        "audit_decision": "uncited_generation_replaced_by_grounded_fallback",
                        "trace": state["trace"]
                        + ["validate_safety_and_citations", "grounded_fallback"],
                    }
            return {
                "status": "abstained",
                "response": add_clinician_notice(failure),
                "audit_decision": "validation_failed",
                "trace": state["trace"] + ["validate_safety_and_citations"],
            }
        return {
            "status": "ok",
            "audit_decision": "grounded_response",
            "trace": state["trace"] + ["validate_safety_and_citations"],
        }

    def write_sanitized_audit(state: TriageState) -> dict:
        status = state.get("status", "error")
        source_ids = [source["source_id"] for source in state.get("sources", [])]
        log_event(
            state["run_id"],
            "sanitized_audit",
            status,
            state.get("audit_decision", "workflow_error"),
            source_ids,
            state["started_at"],
        )
        return {"trace": state["trace"] + ["sanitized_audit"]}

    def after_validation(state: TriageState) -> str:
        return "sanitized_audit" if state["status"] == "blocked" else "consult_record"

    def after_evidence(state: TriageState) -> str:
        return "sanitized_audit" if state["status"] == "abstained" else "generate_contextualized_response"

    workflow = StateGraph(TriageState)
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("consult_record", consult_record)
    workflow.add_node("retrieve_evidence", retrieve_evidence)
    workflow.add_node("assess_evidence", assess_evidence)
    workflow.add_node("generate_contextualized_response", generate_answer)
    workflow.add_node("validate_safety_and_citations", validate_generated_answer)
    workflow.add_node("sanitized_audit", write_sanitized_audit)

    workflow.add_edge(START, "validate_input")
    workflow.add_conditional_edges("validate_input", after_validation)
    workflow.add_edge("consult_record", "retrieve_evidence")
    workflow.add_edge("retrieve_evidence", "assess_evidence")
    workflow.add_conditional_edges("assess_evidence", after_evidence)
    workflow.add_edge("generate_contextualized_response", "validate_safety_and_citations")
    workflow.add_edge("validate_safety_and_citations", "sanitized_audit")
    workflow.add_edge("sanitized_audit", END)
    return workflow.compile()
