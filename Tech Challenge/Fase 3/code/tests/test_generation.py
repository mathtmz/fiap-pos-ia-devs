from pcos_fase3.generation import LocalQwenGenerator


class FakeTokenizer:
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        rendered = "\n".join(f"{item['role']}: {item['content']}" for item in messages)
        return rendered + ("\nassistant:" if add_generation_prompt else "")


def test_langchain_generation_chain_formats_patient_and_sources():
    prompts = []

    def fake_pipeline(prompt, **_kwargs):
        prompts.append(prompt)
        return [{"generated_text": "Resposta sintética [SYN-FAQ-001]."}]

    generator = LocalQwenGenerator(FakeTokenizer(), fake_pipeline)
    answer = generator(
        {
            "question": "Como funciona a demonstração?",
            "patient": {
            "available": True,
            "patient": {
                "patient_id": "SYN-PCOS-01",
                "synthetic_notice": "REGISTRO FICTÍCIO — NÃO É PRONTUÁRIO REAL",
            },
                "pending": ["Avaliação metabólica"],
            },
            "sources": [
                {
                    "source_id": "SYN-FAQ-001",
                    "title": "FAQ: limites do assistente",
                    "version": "2026.1",
                    "publisher": "Equipe do projeto acadêmico",
                    "source_url": "https://example.org/source",
                    "review_status": "resumo não validado",
                    "text": "O conteúdo exige revisão profissional.",
                }
            ],
        }
    )

    assert answer == "Resposta sintética [SYN-FAQ-001]."
    assert len(prompts) == 1
    assert "Como funciona a demonstração?" in prompts[0]
    assert "SYN-PCOS-01" in prompts[0]
    assert "REGISTRO FICTÍCIO" not in prompts[0]
    assert "Avaliação metabólica" in prompts[0]
    assert "SYN-FAQ-001" in prompts[0]
    assert "https://example.org/source" in prompts[0]
    assert "resumo não validado" in prompts[0]
    assert "sintético" not in prompts[0].lower()
    assert "fictício" not in prompts[0].lower()



def test_chain_works_when_langchain_root_lacks_legacy_debug(monkeypatch):
    import sys
    import types
    import langchain_core.globals as langchain_globals

    langchain_module = types.ModuleType("langchain")
    monkeypatch.setitem(sys.modules, "langchain", langchain_module)
    monkeypatch.setattr(langchain_globals, "_HAS_LANGCHAIN", True)
    monkeypatch.setattr(langchain_globals, "langchain", langchain_module, raising=False)
    generator = LocalQwenGenerator(
        FakeTokenizer(), lambda *_args, **_kwargs: [{"generated_text": "Ok"}]
    )

    assert generator({"question": "Teste", "patient": None, "sources": []}) == "Ok"
    assert langchain_module.debug is False
