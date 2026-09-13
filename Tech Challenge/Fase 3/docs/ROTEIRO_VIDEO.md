# Material de gravação — até 15 minutos

| Tempo | Tela/comando | Texto-guia |
|---:|---|---|
| 0:00–1:00 | README e aviso | “Este é um assistente acadêmico; não diagnostica nem prescreve.” |
| 1:00–3:00 | Relatório / diagrama | “Fine-tuning ajusta comportamento; RAG preserva fonte e atualização.” |
| 3:00–5:00 | `python scripts/ingest_corpus.py` | “O corpus da demo é fictício e cada trecho tem ID e versão.” |
| 5:00–6:30 | `python scripts/generate_instruction_data.py` | “São 600 exemplos sintéticos, separados em 420/90/90.” |
| 6:30–8:30 | `streamlit run app.py` | “Seleciono um paciente sintético, pergunto sobre limites e vejo fontes e percurso.” |
| 8:30–10:00 | Streamlit: pedido de dose | “A recusa ocorre antes de consultar qualquer dado.” |
| 10:00–11:30 | `pytest -q` | “Testes cobrem PII, injection, prescrição, abstinência e logs.” |
| 11:30–13:00 | `python scripts/run_evaluation.py` | “Mostro métricas de retrieval e não alego métricas clínicas.” |
| 13:00–15:00 | Limitações | “O corpus é mínimo, o treino GPU é opcional e a validação humana é obrigatória.” |

## Sequência de slides

1. Problema, escopo e limites clínicos.
2. Arquitetura LangChain/LangGraph e controles de segurança.
3. Dados sintéticos, proveniência e split de fine-tuning.
4. Demonstração: resposta com fontes, pendência simulada, recusa.
5. Tabela Precision@k/Recall@k/MRR e rubrica de geração.
6. Limitações, riscos e próximos passos.

## Checklist

- [ ] Rodar ingestão, geração de exemplos, testes e avaliação.
- [ ] Mostrar a fonte, versão e trecho recuperado.
- [ ] Mostrar o trace LangGraph e o log sanitizado.
- [ ] Mostrar recusa de PII, injection e prescrição.
- [ ] Declarar dados fictícios, limitações e validação humana.
