# Contexto da Fase 3 — IA Generativa

Estado consolidado em 15/09/2026. O enunciado oficial está em [8IADT - Fase 3 - Tech challenge.pdf](../../Materiais/Fase%203%20-%20Generative%20AI/Tech%20Challenge/8IADT%20-%20Fase%203%20-%20Tech%20challenge.pdf).

## Escopo e entregas solicitadas

O desafio solicita fine-tuning de um LLM, assistente integrado a LangChain e base estruturada, fluxos automatizados com LangGraph, salvaguardas, auditoria e fontes, código modular com README, relatório técnico com avaliação e vídeo demonstrativo de até 15 minutos.

O protótipo acadêmico organiza evidências sobre SOP/PCOS. Inclui solicitações sobre hipótese diagnóstica, prescrição e dose como rascunhos para revisão médica. Como os resumos do corpus local não têm validação clínica, o assistente não os utiliza para fundamentar conclusões individuais; informa a limitação e se abstém. A decisão clínica final cabe ao médico responsável.

## Implementação e dados

O repositório inclui 12 registros de demonstração em SQLite, quatro notas internas, cinco referências institucionais rastreáveis, 44 perguntas de avaliação de recuperação e 600 exemplos instrucionais sintéticos divididos em 420/90/90. Notícias, exemplos financeiros e textos literários dos materiais didáticos não integram o corpus médico ou o treinamento.

A interface Streamlit aciona um fluxo LangGraph com validação de entradas, consulta parametrizada ao SQLite, recuperação lexical, avaliação de evidências, chain LangChain, checagem de citações e auditoria sanitizada. Respostas do modelo sem citação recuperada válida são descartadas; o fluxo pode usar uma saída determinística fundamentada, registrada como `grounded_fallback`. A auditoria não armazena pergunta nem identificador do paciente.

O QLoRA de `Qwen/Qwen2.5-0.5B-Instruct` foi executado no Colab com GPU Tesla T4 por duas épocas. As perdas registradas foram 2,7671 no treino, 2,6078 na validação e 2,4071 no teste. São métricas de otimização do conjunto sintético.

## Resultados

A recuperação obteve Precision@3 0,326, Recall@3 0,943 e MRR 0,879 nos 44 casos. Nos 20 casos específicos sobre referências institucionais, o documento esperado apareceu no top 3. A comparação de geração contém 90 perguntas e 270 respostas nas condições modelo-base sem RAG, LoRA sem RAG e LoRA com RAG. As citações válidas foram identificadas em 1/90, 0/90 e 0/90 respostas, respectivamente. A análise por rubrica é exploratória e não demonstra benefício ou segurança clínica; uma revisão manual complementar não é exigida explicitamente pelo enunciado.

Os 48 testes automatizados passaram na execução local consolidada. O modelo e o adaptador foram carregados em CPU no smoke test; uma resposta sem citação foi descartada e substituída pelo caminho `grounded_fallback`.

## Situação da entrega

O código, os dados de demonstração, o adaptador, a avaliação, o README, o relatório técnico e o roteiro estão organizados no repositório. Falta gravar e conferir o vídeo demonstrativo de até 15 minutos. A sequência e as falas sugeridas estão em [docs/ROTEIRO_VIDEO.md](./docs/ROTEIRO_VIDEO.md). A revisão manual complementar das 270 respostas pode ampliar a análise, mas não constitui pendência formal do desafio.

Os resultados têm finalidade acadêmica e de engenharia. O corpus é pequeno, o mecanismo de recuperação é lexical e os resumos locais não foram revisados clinicamente. O protótipo não foi validado para uso clínico. Consulte o [relatório técnico](./docs/RELATORIO_TECNICO.md), o [inventário de fontes](./docs/FONTES_CLINICAS.md) e o [README](./README.md) para detalhes e reprodução.
