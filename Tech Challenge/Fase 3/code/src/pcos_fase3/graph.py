"""Typed triage workflow. Uses a deterministic, testable generator; LangGraph is optional at runtime."""
import time
from typing import TypedDict

from .audit import log_event, new_run_id
from .models import TriageRequest
from .patient_store import patient_summary
from .retrieval import retrieve
from .safety import safety_decision, validate_answer


class TriageState(TypedDict, total=False):
    request: TriageRequest
    run_id: str
    trace: list[str]
    patient: dict
    sources: list[dict]
    response: str
    status: str


def _answer(state: TriageState) -> str:
    sources = state["sources"]
    snippets = " ".join(f"{source['text']} [{source['source_id']}]" for source in sources)
    pending = state["patient"].get("pending", [])
    pending_note = " Há pendência simulada: " + ", ".join(pending) + "." if pending else ""
    return ("Resposta educacional, não diagnóstica: com base apenas nas fontes recuperadas, " + snippets + pending_note +
            " As opções descritas exigem avaliação e validação por profissional habilitado.")


def run_triage(payload: dict | TriageRequest) -> dict:
    request = payload if isinstance(payload, TriageRequest) else TriageRequest.model_validate(payload)
    run_id, trace, started = new_run_id(), [], time.perf_counter()
    trace.append("validate_input")
    decision = safety_decision(request.question)
    if decision:
        log_event(run_id, "validate_input", "blocked", "safety_refusal", [], started)
        return {"status": "blocked", "response": decision, "sources": [], "trace": trace, "run_id": run_id}
    trace.append("consult_synthetic_record")
    patient = patient_summary(request.patient_id)
    trace.append("retrieve_evidence")
    sources = retrieve(request.question)
    if not sources:
        trace.append("abstain")
        response = "Não há evidência suficiente no corpus local para responder com segurança. Consulte fontes revisadas e um profissional de saúde."
        log_event(run_id, "abstain", "abstained", "insufficient_evidence", [], started)
        return {"status": "abstained", "response": response, "sources": [], "patient": patient, "trace": trace, "run_id": run_id}
    trace.extend(["assess_evidence", "generate_contextualized_response", "validate_safety_and_citations"])
    response = _answer({"sources": sources, "patient": patient})
    failure = validate_answer(response, sources)
    if failure:
        log_event(run_id, "validate_safety_and_citations", "abstained", "validation_failed", [item["source_id"] for item in sources], started)
        return {"status": "abstained", "response": failure, "sources": sources, "patient": patient, "trace": trace, "run_id": run_id}
    trace.append("sanitized_audit")
    log_event(run_id, "sanitized_audit", "ok", "grounded_response", [item["source_id"] for item in sources], started)
    return {"status": "ok", "response": response, "sources": sources, "patient": patient, "trace": trace, "run_id": run_id}


def build_langgraph():
    """Expose the same stages as a LangGraph graph when the optional dependency is installed."""
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:  # pragma: no cover - dependency-specific path
        raise RuntimeError("Instale langgraph para materializar o grafo visual.") from exc

    def validate(state: TriageState):
        decision = safety_decision(state["request"].question)
        return {"status": "blocked" if decision else "ok", "response": decision or "", "trace": state.get("trace", []) + ["validate_input"]}

    def record(state: TriageState):
        return {"patient": patient_summary(state["request"].patient_id), "trace": state["trace"] + ["consult_synthetic_record"]}

    def evidence(state: TriageState):
        return {"sources": retrieve(state["request"].question), "trace": state["trace"] + ["retrieve_evidence"]}

    def assess(state: TriageState):
        return {"status": "ok" if state["sources"] else "abstained", "trace": state["trace"] + ["assess_evidence"]}

    def generate(state: TriageState):
        return {"response": _answer(state), "trace": state["trace"] + ["generate_contextualized_response"]}

    def review(state: TriageState):
        failure = validate_answer(state["response"], state["sources"])
        return {"status": "abstained" if failure else "ok", "response": failure or state["response"], "trace": state["trace"] + ["validate_safety_and_citations"]}

    def audit(state: TriageState):
        return {"trace": state["trace"] + ["sanitized_audit"]}

    workflow = StateGraph(TriageState)
    workflow.add_node("validate_input", validate)
    workflow.add_node("consult_synthetic_record", record)
    workflow.add_node("retrieve_evidence", evidence)
    workflow.add_node("assess_evidence", assess)
    workflow.add_node("generate_contextualized_response", generate)
    workflow.add_node("validate_safety_and_citations", review)
    workflow.add_node("sanitized_audit", audit)
    workflow.add_edge(START, "validate_input")
    workflow.add_conditional_edges("validate_input", lambda s: END if s["status"] == "blocked" else "consult_synthetic_record")
    workflow.add_edge("consult_synthetic_record", "retrieve_evidence")
    workflow.add_edge("retrieve_evidence", "assess_evidence")
    workflow.add_conditional_edges("assess_evidence", lambda s: END if s["status"] == "abstained" else "generate_contextualized_response")
    workflow.add_edge("generate_contextualized_response", "validate_safety_and_citations")
    workflow.add_edge("validate_safety_and_citations", "sanitized_audit")
    workflow.add_edge("sanitized_audit", END)
    return workflow.compile()
