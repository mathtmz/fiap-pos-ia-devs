# Contexto da Fase 3 — IA Generativa

> Propósito: contexto operacional para orientar implementação, documentação e decisões técnicas da Fase 3.
>
> Status: criado a partir de todo o material disponível em `/Users/matomaz/Projects/FIAP/Tech Challenge/Fase 3 - Generative AI/`. Não foi localizado um enunciado oficial separado do Tech Challenge; portanto, nenhum item abaixo deve ser interpretado como requisito avaliativo oficial sem confirmação posterior.

## 1. Leitura executiva

A Fase 3 concentra-se em aplicações de IA generativa baseadas em LLMs: prompt engineering, uso responsável de modelos, preparação de dados, fine-tuning, RAG, LangChain, LangGraph e sistemas multiagente.

A continuidade natural com as fases anteriores é evoluir o projeto de apoio à triagem de SOP para uma camada generativa **ancorada em conhecimento confiável**, sem transformar o sistema em diagnóstico autônomo. A escolha de escopo permanece pendente do enunciado oficial.

Para este repositório, a direção técnica mais consistente é iniciar por **RAG avaliável e com fontes**, usando corpus autorizado e desidentificado. Fine-tuning só deve ser considerado quando houver uma tarefa estável, exemplos de alta qualidade suficientes e uma hipótese mensurável de ganho que RAG e prompting não resolvam.

## 2. O que já existe no repositório

| Fase | Estado | Ativos reutilizáveis |
| --- | --- | --- |
| 1 | Concluída | Dataset PCOS, notebook, modelos clássicos, métricas, SHAP e discussão clínica. |
| 2 | Concluída | Pipeline Python modular, artefatos de experimentos, tracking local, testes, explicação por LLM e restrições de uso em saúde. |
| 3 | Inicial | Apenas estrutura e este contexto; não há código, corpus ou requisito oficial versionado. |

Limites herdados importantes:

- O sistema é apoio à triagem, não diagnóstico, prescrição ou conduta médica.
- O dataset histórico possui 541 pacientes e não tem validação prospectiva ou externa.
- Resultados e explicações precisam declarar incertezas, limitações e necessidade de avaliação profissional.
- Não usar dados clínicos identificáveis em corpus, logs, prompts ou provedores externos.

## 3. Mapa do material estudado

| Bloco | Conteúdos aplicáveis |
| --- | --- |
| Matéria 1 — ChatGPT e LLMs | Fundamentos de IA generativa; Chain of Thought como técnica de raciocínio; ética, vieses, privacidade, alucinações, prompt injection, agentes e ferramentas externas. |
| Matéria 2 — Guia de prompts | Objetivo, contexto, instruções, formato de saída e iteração de prompts; avaliação quantitativa e qualitativa; uso de IA no ciclo de software. |
| Matéria 3 — Fine-tuning e RAG | Coleta e limpeza de dados, geração de exemplos, foundation models, tokenização, embeddings, quantização, PEFT/LoRA, banco vetorial e RAG. |
| Matéria 4 — LangChain | Componentes e chains, carregadores de documentos, templates, parsing, routing, memória e agentes com ferramentas/banco de dados. |
| Matéria 5 — LangGraph | Grafos dirigidos com estado tipado, nós, arestas condicionais, ciclos, checkpointing, RAG em grafo, avaliação, monitoramento, ReAct e coordenação multiagente. |

### Materiais complementares relevantes

- Fine-tuning: exemplo completo de coleta de notícias, geração de saídas, preparação de `jsonl` e adaptação de sumarizador.
- RAG: exemplo com corpus textual, embeddings, FAISS, recuperação e resposta contextualizada.
- LangGraph: exemplos de fluxo tipado, condicionais, RAG com fontes e comparação sem-RAG versus com-RAG.
- Multiagente: pesquisador, analista e relator coordenados por estado compartilhado e rotas condicionais.

## 4. Conceitos que devem aparecer na solução

### Prompt engineering

Um prompt de produção deve explicitar:

1. papel e escopo do assistente;
2. tarefa objetiva;
3. contexto permitido e fontes;
4. regras de segurança e de recusa;
5. formato estruturado de saída;
6. comportamento diante de evidência ausente ou insuficiente.

Prompts devem ser versionados e avaliados com casos representativos, não apenas demonstrados em exemplos favoráveis.

### RAG

Fluxo-base recomendado:

```text
Corpus autorizado
  → extração/limpeza
  → divisão em chunks + metadados
  → embeddings + índice vetorial
  → recuperação/re-ranking
  → prompt com contexto recuperado
  → resposta com citações e comportamento de abstinência
```

Componentes esperados:

- documentos rastreáveis, com origem, versão e data;
- chunking compatível com o tipo de fonte;
- embeddings e vector store;
- recuperação de `k` documentos, opcionalmente com re-ranking;
- resposta limitada ao contexto recuperado quando o caso exigir factualidade;
- fontes/chunks retornados ao usuário ou registrados para auditoria.

### Fine-tuning

Fine-tuning adapta um foundation model a tarefa ou estilo específico. Exige dados bem curados, separados em treino/validação/teste e avaliação contra um baseline. PEFT/LoRA reduzem custo ao treinar adaptadores em vez do modelo inteiro; quantização reduz uso de memória.

Não usar fine-tuning para substituir uma base de conhecimento mutável ou para compensar documentação ruim. Para perguntas baseadas em diretrizes e literatura, RAG tende a oferecer atualização e rastreabilidade melhores.

### LangChain e LangGraph

- LangChain serve para componentes reutilizáveis: loaders, splitters, prompts, modelos, retrievers, parsers e ferramentas.
- LangGraph é justificável quando há estado compartilhado, bifurcações, repetição, tratamento de falha, persistência, paralelismo controlado ou múltiplos papéis.
- Um fluxo linear simples não precisa ser convertido em multiagente.
- O estado do grafo deve ser tipado, mínimo e separado entre entrada, contexto recuperado, resposta, fontes, status e erro.

## 5. Opção de projeto recomendada — ainda sujeita ao enunciado

### Assistente de evidências para apoio à triagem de SOP

O assistente recebe uma pergunta de caráter educacional ou clínico não identificável, recupera trechos de fontes selecionadas e responde de forma didática, citando o material utilizado. Ele não produz diagnóstico, tratamento ou recomendação individual definitiva.

Fluxo sugerido:

```text
Pergunta
  → validação e classificação de escopo
  → retrieve (corpus clínico curado)
  → verificação de relevância/cobertura
  → geração ancorada em fontes
  → checagem de segurança e completude
  → resposta + fontes | abstinência/escalonamento
```

Possíveis nós LangGraph:

| Nó | Responsabilidade |
| --- | --- |
| `validate_input` | Rejeitar PII, pedidos de diagnóstico/prescrição e entradas fora de escopo. |
| `retrieve` | Recuperar chunks e metadados do corpus. |
| `assess_evidence` | Verificar relevância, quantidade e confiança do contexto. |
| `generate` | Responder apenas com base nas fontes recuperadas. |
| `review` | Conferir citações, linguagem segura e ausência de afirmações não sustentadas. |
| `abstain` | Explicar falta de evidência e orientar busca de fonte/profissional apropriado. |

Um único agente com essas etapas explícitas é suficiente inicialmente. Multiagente só deve ser usado se houver especialização real e critérios claros de coordenação.

## 6. Segurança, privacidade e ética por padrão

Como o domínio é saúde, estes controles são parte do desenho, não acabamento:

- corpus apenas de fontes autorizadas, versionadas e revisáveis;
- remover ou não coletar dados pessoais e identificadores;
- chaves em variáveis de ambiente, nunca no repositório ou em logs;
- proteger contra prompt injection: documentos recuperados são dados, não instruções confiáveis;
- separar instruções de sistema, entrada do usuário e contexto RAG;
- limitar ferramentas e ações a allowlists; não permitir execução arbitrária;
- exigir fonte para afirmações factuais e responder com abstinência quando não houver evidência;
- registrar métricas e eventos sanitizados, sem dados clínicos identificáveis;
- comunicar que o resultado é educacional/de apoio e requer avaliação profissional quando aplicável.

## 7. Avaliação obrigatória da qualidade técnica

Avaliar o sistema por camadas:

| Camada | Pergunta de avaliação | Exemplos de métricas/evidências |
| --- | --- | --- |
| Recuperação | Os documentos relevantes chegam ao contexto? | Precision@k, Recall@k, MRR/nDCG, avaliação humana dos chunks. |
| Geração | A resposta é fiel ao contexto e útil? | groundedness/fidelidade, completude, correção factual, clareza, ROUGE quando houver referência apropriada. |
| Segurança | O sistema recusa ou redireciona solicitações perigosas? | testes de prompt injection, PII, diagnóstico/prescrição, ausência de fonte e casos adversariais. |
| Operação | O fluxo funciona com desempenho aceitável? | latência de retrieval/geração, taxa de abstinência, erros, custo/tokens, feedback. |

Construir um conjunto de avaliação versionado, com perguntas, resposta/trecho esperado, fontes relevantes e classificação de risco. Separar casos de desenvolvimento dos usados para reportar resultado final.

## 8. Estrutura do projeto

```text
Tech Challenge/Fase 3/
├── README.md
├── CONTEXTO_FASE3_IA_GENERATIVA.md
├── data/
│   ├── raw/                  # fontes autorizadas; não versionar dados sensíveis
│   ├── processed/            # chunks e metadados tratados
│   └── eval/                 # conjunto de avaliação versionado
└── code/
    ├── requirements.txt
    ├── .env.example
    ├── src/
    │   └── pcos_fase3/
    │       ├── config.py
    │       ├── ingestion.py
    │       ├── retrieval.py
    │       ├── prompts.py
    │       ├── graph.py
    │       ├── safety.py
    │       └── evaluation.py
    ├── scripts/
    │   ├── ingest_corpus.py
    │   ├── build_index.py
    │   ├── run_evaluation.py
    │   └── run_demo.py
    ├── tests/
    └── outputs/
        ├── figures/
        ├── metrics/
        └── reports/
```

Os diretórios já criados representam a base mínima; os arquivos de implementação devem ser adicionados somente depois da definição do escopo e do corpus.

## 9. Plano de execução recomendado

1. Registrar o enunciado oficial quando disponível e converter seus requisitos em checklist verificável.
2. Definir usuário, pergunta atendida, limite clínico e critério de sucesso.
3. Selecionar e versionar corpus autorizado; definir política de atualização e metadados.
4. Implementar baseline sem RAG e baseline RAG simples.
5. Criar conjunto de avaliação antes de otimizar prompts ou arquitetura.
6. Medir recuperação, fidelidade, segurança, latência e custo.
7. Adicionar LangGraph para condicionalidade, validação e abstinência; usar multiagente apenas se necessário.
8. Comparar baselines, documentar falhas e produzir relatório técnico/reprodutível.

## 10. Decisões pendentes

- Qual é o enunciado e quais entregáveis serão avaliados?
- O projeto deve obrigatoriamente usar fine-tuning, RAG, LangChain ou LangGraph?
- Qual corpus será permitido e como sua licença, proveniência e atualização serão registradas?
- A experiência será apenas por script/notebook ou incluirá interface/API?
- Qual provedor/modelo, orçamento e política de uso de dados serão adotados?
- Qual nível de personalização clínica é permitido sem ultrapassar o escopo de apoio educacional?

## 11. Critério de pronto proposto

- [ ] Enunciado oficial incorporado ao repositório e requisitos mapeados.
- [ ] Escopo e limites clínicos documentados.
- [ ] Corpus autorizado, desidentificado e rastreável.
- [ ] Baseline e RAG comparados em conjunto de avaliação separado.
- [ ] Respostas apresentam fontes ou abstinência explícita.
- [ ] Casos de segurança e prompt injection cobertos por testes.
- [ ] Métricas de recuperação, geração, segurança e operação registradas.
- [ ] Código, prompts, dependências e instruções de execução são reproduzíveis.
- [ ] Relatório descreve ganhos, falhas, limitações e próximos passos.

## 12. Referência de origem

Material analisado: 23 PDFs de aula, notebooks e datasets complementares presentes em `/Users/matomaz/Projects/FIAP/Tech Challenge/Fase 3 - Generative AI/`.

Tópicos cobertos: LLMs, ética e segurança, prompt engineering, web scraping e preparação de dados, fine-tuning com Llama/LoRA/PEFT, embeddings, FAISS e RAG, LangChain, LangGraph, estado persistente, agentes, ferramentas, ReAct, avaliação e monitoramento.
