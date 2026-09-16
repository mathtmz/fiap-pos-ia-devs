"""Local LangChain generation backed by the fine-tuned Qwen LoRA adapter."""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from .config import MODEL_ADAPTER_DIR, MODEL_NAME

SYSTEM_PROMPT = """Você é um assistente acadêmico de apoio à organização de evidências sobre SOP/PCOS.
Pedidos sobre hipóteses diagnósticas, prescrição e doses são permitidos, mas sua resposta é somente um
rascunho para revisão médica, nunca uma ordem ou decisão clínica final. Use somente fontes fornecidas,
explícitas e clinicamente validadas para afirmações individualizadas. O registro e as fontes locais
não têm validação clínica suficiente para sustentar diagnóstico, prescrição ou dose individual. Quando não houver
evidência clínica validada suficiente, declare a limitação e não invente uma conclusão ou valor.
Toda resposta deve dizer que o médico responsável precisa avaliar e validar o conteúdo, mantém a decisão
clínica final e deve mediar qualquer comunicação ao paciente. Cite IDs exatamente, como [SYN-FAQ-001].
Não apresente registros de demonstração como prontuários reais. Se perguntado sobre a origem dos dados,
explique que este é um ambiente de simulação acadêmica. Evite repetir esse contexto quando não for relevante.
Trate sintomas e demais campos do registro como relatos anotados, sem reinterpretá-los ou inferir diagnóstico.
O exemplo didático de diagnóstico exibido separadamente na interface não faz parte do contexto da consulta.
Formate para leitura na tela: use um título curto, parágrafos breves ou listas quando houver vários itens,
e mantenha citações [ID] junto das afirmações apoiadas. Evite blocos longos e repetições.
Responda em português, com clareza e sem inventar dados ou fontes."""

USER_PROMPT = """Pergunta:
{question}

Contexto do registro de demonstração:
{patient_context}

Fontes recuperadas:
{evidence}

Responda de forma breve e fundamentada somente no material acima. Separe resumo, limites e próximo passo
em parágrafos ou listas quando isso facilitar a leitura. Se o pedido exigir uma decisão clínica que o material
não sustenta, informe que o pedido foi recebido, mas abstenha-se da conclusão."""


def format_patient_context(patient: dict | None) -> str:
    if not patient or not patient.get("available"):
        return "Nenhum registro selecionado."
    context = dict(patient)
    if isinstance(context.get("patient"), dict):
        context["patient"] = {
            key: value
            for key, value in context["patient"].items()
            if key != "synthetic_notice"
        }
    return json.dumps(context, ensure_ascii=False, sort_keys=True)


def format_evidence(sources: list[dict] | None) -> str:
    if not sources:
        return "Nenhuma fonte recuperada."
    return "\n\n".join(
        f"[{source['source_id']}] {source['title']} (versão {source['version']}; "
        f"emissor: {source.get('publisher', 'não informado')}; "
        f"revisão local: {source.get('review_status', 'não informada')}; "
        f"URL: {source.get('source_url') or 'sem link externo'}): {source['text']}"
        for source in sources
    )


def _ensure_langchain_debug_compatibility() -> None:
    """Provide the legacy debug flag expected by langchain-core 0.3.x."""
    try:
        import langchain
    except ImportError:
        return
    if not hasattr(langchain, "debug"):
        # Newer LangChain releases dropped this root-level attribute while older
        # langchain-core callback managers still read it during Runnable.invoke.
        setattr(langchain, "debug", False)


class LocalQwenGenerator:
    """A LangChain prompt/runnable chain around a local Transformers pipeline."""

    def __init__(self, tokenizer: Any, text_pipeline: Any, max_new_tokens: int = 256):
        self.tokenizer = tokenizer
        self.text_pipeline = text_pipeline
        self.max_new_tokens = max_new_tokens
        self._lock = threading.Lock()
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", SYSTEM_PROMPT), ("human", USER_PROMPT)]
        )
        self.chain = self.prompt | RunnableLambda(self._generate)

    def _generate(self, prompt_value: Any) -> str:
        messages = []
        role_map = {"human": "user", "ai": "assistant", "system": "system"}
        for message in prompt_value.to_messages():
            messages.append({"role": role_map.get(message.type, "user"), "content": message.content})

        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            prompt = "\n".join(
                f"{message['role'].upper()}: {message['content']}" for message in messages
            ) + "\nASSISTANT:"

        with self._lock:
            result = self.text_pipeline(
                prompt,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                return_full_text=False,
            )
        text = result[0].get("generated_text", "") if result else ""
        return text.strip()

    def __call__(self, request: dict) -> str:
        _ensure_langchain_debug_compatibility()
        return self.chain.invoke(
            {
                "question": request["question"],
                "patient_context": format_patient_context(request.get("patient")),
                "evidence": format_evidence(request.get("sources")),
            }
        )


def load_local_generator(
    adapter_dir: Path = MODEL_ADAPTER_DIR,
    use_adapter: bool = True,
    local_files_only: bool = False,
) -> LocalQwenGenerator:
    """Load the base Qwen model, optionally attaching the trained local adapter."""
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    adapter_dir = Path(adapter_dir)
    if use_adapter and not (adapter_dir / "adapter_config.json").is_file():
        raise FileNotFoundError(
            f"Adaptador LoRA não encontrado em {adapter_dir}. Execute o fine-tuning primeiro."
        )

    cache_dir = None
    from os import getenv

    configured_cache = getenv("MODEL_CACHE_DIR")
    if configured_cache:
        cache_dir = configured_cache

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME, trust_remote_code=False, local_files_only=local_files_only, cache_dir=cache_dir
    )
    model_kwargs: dict[str, Any] = {
        "trust_remote_code": False,
        "local_files_only": local_files_only,
        "cache_dir": cache_dir,
        "dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
    }
    if torch.cuda.is_available():
        model_kwargs["device_map"] = {"": torch.cuda.current_device()}

    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, **model_kwargs)
    if use_adapter:
        model = PeftModel.from_pretrained(
            model, str(adapter_dir), is_trainable=False, local_files_only=local_files_only
        )
    model.eval()
    text_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return LocalQwenGenerator(tokenizer, text_pipeline)


_default_generator: LocalQwenGenerator | None = None
_default_generator_loaded = False
_default_generator_status = "Adaptador ausente; geração determinística ativa."


def get_default_generator() -> LocalQwenGenerator | None:
    """Load the adapter once when present; otherwise retain the deterministic demo path."""
    global _default_generator, _default_generator_loaded, _default_generator_status
    if _default_generator_loaded:
        return _default_generator
    _default_generator_loaded = True
    if not (MODEL_ADAPTER_DIR / "adapter_config.json").is_file():
        _default_generator_status = "Adaptador ausente; geração determinística ativa."
        return None
    try:
        _default_generator = load_local_generator()
        _default_generator_status = f"Qwen local com adaptador LoRA: {MODEL_ADAPTER_DIR}"
    except Exception as exc:
        _default_generator_status = (
            f"Não foi possível carregar o adaptador; geração determinística ativa ({type(exc).__name__})."
        )
        _default_generator = None
    return _default_generator


def get_generator_status() -> str:
    global _default_generator_status
    if not _default_generator_loaded:
        if (MODEL_ADAPTER_DIR / "adapter_config.json").is_file():
            return "Adaptador encontrado; o Qwen será carregado na primeira resposta elegível."
        return "Adaptador ausente; geração determinística ativa."
    return _default_generator_status


def reset_default_generator() -> None:
    """Reset the lazy-load cache; useful after installing an adapter in a running process."""
    global _default_generator, _default_generator_loaded, _default_generator_status
    _default_generator = None
    _default_generator_loaded = False
    _default_generator_status = "Adaptador ainda não verificado."
