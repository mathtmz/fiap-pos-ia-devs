# Contexto Otimizado para IA - Tech Challenge Fase 2

Este documento consolida o enunciado do Tech Challenge da Fase 2 e o conteudo das aulas da fase. O objetivo e servir como briefing tecnico para orientar a implementacao de um bom challenge, reaproveitando o projeto da Fase 1 sobre diagnostico de SOP/PCOS com Machine Learning.

## 1. Leitura Executiva

O Tech Challenge da Fase 2 pede uma solucao que una:

- Algoritmos geneticos para otimizacao.
- Processamento de linguagem natural e/ou LLMs para explicacao, interpretacao ou geracao textual.
- Boa organizacao de codigo Python, documentacao, testes e demonstracao.
- Opcionalmente, arquitetura em nuvem, monitoramento, logging e autoescalabilidade.

O enunciado oferece dois caminhos:

1. **Projeto 1 - Otimizacao de modelos de diagnostico**
   - Continuar os modelos medicos da Fase 1.
   - Usar algoritmos geneticos para otimizar hiperparametros.
   - Integrar LLM para explicar diagnosticos e resultados para profissionais de saude.

2. **Projeto 2 - Otimizacao de rotas medicas**
   - Resolver TSP/VRP para distribuicao de medicamentos e insumos.
   - Usar algoritmo genetico para rotas com restricoes.
   - Integrar LLM para gerar instrucoes de entrega e relatorios.

**Recomendacao:** seguir com o **Projeto 1**. Ele aproveita diretamente o trabalho da Fase 1, reduz risco de escopo e cria continuidade narrativa: primeiro foi construido um sistema de apoio ao diagnostico de SOP; agora ele sera aprimorado com otimizacao evolutiva e interpretabilidade em linguagem natural.

## 2. O que Precisa Ser Feito no Projeto 1

### 2.1 Requisitos Obrigatorios do Enunciado

Implementar um algoritmo genetico para otimizar hiperparametros dos modelos de diagnostico da Fase 1:

- Definir codificacao dos genes para hiperparametros relevantes.
- Implementar selecao.
- Implementar cruzamento/crossover.
- Implementar mutacao.
- Definir funcao fitness baseada em metricas do modelo, como accuracy, recall, F1-score e/ou AUC.
- Comparar modelos otimizados contra modelos originais.
- Realizar ao menos 3 experimentos com configuracoes diferentes do algoritmo genetico, por exemplo:
  - tamanho da populacao;
  - taxa de mutacao;
  - taxa de crossover;
  - numero de geracoes;
  - elitismo.

Implementar recursos de acompanhamento:

- Monitoramento e logging de desempenho.
- Registro de experimentos, melhor individuo, historico de fitness e metricas finais.
- Documentacao de arquitetura e decisoes.

Integrar uma LLM pre-treinada:

- Gerar explicacoes em linguagem natural para diagnosticos produzidos pelos modelos.
- Transformar metricas e dados numericos em insights acionaveis para medicos.
- Preparar a base para futura integracao com dados textuais no Modulo 3.
- Aplicar prompt engineering.
- Avaliar a qualidade das interpretacoes geradas.

Organizacao para ambos os projetos:

- Projeto Python bem estruturado.
- Ambiente virtual com Poetry, Pipenv ou venv.
- Documentacao detalhada, incluindo diagrama de arquitetura.
- Testes automatizados.
- Scripts ou notebooks de demonstracao.
- Relatorio tecnico.
- Video de ate 15 minutos.

## 3. Decisao de Produto Recomendada

### Tema

**Otimizacao evolutiva e explicabilidade generativa para diagnostico de SOP.**

### Proposta

Evoluir o sistema da Fase 1 para uma aplicacao de experimentacao e interpretabilidade:

1. Carregar o dataset de PCOS/SOP.
2. Reproduzir o pipeline da Fase 1.
3. Treinar baselines originais.
4. Rodar algoritmo genetico para buscar hiperparametros melhores.
5. Comparar metricas antes/depois.
6. Gerar explicacoes com LLM para:
   - desempenho global dos modelos;
   - previsao individual de paciente;
   - top features e SHAP;
   - recomendacoes de uso clinico com ressalvas.

### Por que essa escolha e forte

- Reaproveita dataset, conhecimento clinico, features e modelos da Fase 1.
- Atende diretamente o Projeto 1 do enunciado.
- Permite demonstrar AG de forma clara e mensuravel.
- Permite integrar LLM de forma util, nao cosmetica.
- Cria uma narrativa academica consistente: diagnostico, otimizacao, interpretabilidade, riscos e limites.

## 4. Arquitetura Recomendada

```text
fase2/
├── README.md
├── pyproject.toml ou requirements.txt
├── data/
│   └── PCOS_data_without_infertility.xlsx
├── scripts/
│   ├── run_baseline.py
│   ├── run_ga_experiments.py
│   ├── finalize_ga_results.py
│   └── generate_llm_report.py
├── src/
│   ├── data/
│   │   ├── loader.py
│   │   └── preprocessing.py
│   ├── models/
│   │   ├── baseline.py
│   │   ├── training.py
│   │   └── evaluation.py
│   ├── genetic/
│   │   ├── chromosome.py
│   │   ├── fitness.py
│   │   ├── selection.py
│   │   ├── crossover.py
│   │   ├── mutation.py
│   │   └── optimizer.py
│   ├── llm/
│   │   ├── prompts.py
│   │   ├── provider.py
│   │   └── evaluator.py
│   ├── explainability/
│   │   ├── shap_utils.py
│   │   └── reports.py
│   └── monitoring/
│       ├── logger.py
│       └── experiment_tracker.py
├── tests/
│   ├── test_chromosome.py
│   ├── test_genetic_operators.py
│   ├── test_fitness.py
│   └── test_prompts.py
├── reports/
│   ├── RELATORIO_TECNICO.md
│   └── images/
└── scripts/
    ├── run_baseline.py
    ├── run_ga_experiments.py
    └── generate_llm_report.py
```

## 5. Pipeline Tecnico Proposto

### 5.1 Dados e Pre-processamento

Base da Fase 1:

- Dataset Kaggle PCOS.
- 541 pacientes.
- Target: `PCOS (Y/N)`.
- Classe positiva: paciente com SOP.
- Desequilibrio moderado: aproximadamente 67% sem SOP e 33% com SOP.

Manter as decisoes da Fase 1:

- Remover identificadores (`Sl. No`, `Patient File No.`) e coluna vazia.
- Corrigir tipos mistos em `AMH(ng/mL)` e `II beta-HCG`.
- Imputar ausentes com mediana.
- Aplicar feature engineering:
  - `total_foliculos`;
  - `soma_sintomas`;
  - `faixa_imc`;
  - `razao_lh_fsh`.
- Separar treino/teste estratificado.
- Aplicar `StandardScaler` com fit apenas no treino.

### 5.2 Modelos Baseline

Usar os modelos da Fase 1 como referencia:

- Regressao Logistica.
- Arvore de Decisao.
- Random Forest.
- KNN.

Ponto de partida recomendado para otimizacao genetica:

- Focar em **Random Forest** e **Regressao Logistica**.
- Random Forest tem melhor F1/acuracia na Fase 1.
- Regressao Logistica tem melhor recall da classe positiva, metricamente importante em contexto medico.

### 5.3 Metrica Principal

O enunciado permite accuracy, recall, F1-score etc. Para esse dominio, a metrica deve priorizar recall:

- Falso negativo = paciente com SOP classificada como saudavel.
- Em triagem medica, falso negativo e mais grave que falso positivo.

Funcao fitness recomendada:

```text
fitness = 0.50 * recall_pos + 0.30 * f1_pos + 0.15 * auc_roc + 0.05 * accuracy - penalidade_overfit
```

Penalidade de overfit:

```text
penalidade_overfit = max(0, f1_treino - f1_validacao - tolerancia) * peso
```

Alternativa mais simples:

```text
fitness = recall_pos
```

Mas a alternativa composta e mais robusta para relatorio tecnico.

## 6. Algoritmo Genetico para Hiperparametros

### 6.1 Conceitos das Aulas Aplicados

Das aulas de Algoritmo Genetico:

- Otimizacao pode ser exata ou heuristica.
- AG e heuristica bioinspirada adequada quando busca exata e cara.
- Individuo representa uma solucao candidata.
- Genes representam caracteristicas da solucao.
- Populacao e conjunto de individuos.
- Fitness mede qualidade da solucao.
- Selecao privilegia individuos mais aptos.
- Crossover combina material genetico.
- Mutacao injeta diversidade.
- Elitismo preserva boas solucoes.
- Convergencia precisa equilibrar exploracao e aproveitamento.
- Populacao grande aumenta diversidade, mas custa mais.
- Populacao pequena converge rapido, mas pode cair em otimos locais.
- Mutacao alta explora mais, mas pode destruir boas solucoes.
- Mutacao baixa explora menos e pode convergir cedo.

### 6.2 Codificacao dos Genes

Para Random Forest:

```python
{
    "n_estimators": int,        # 50 a 500
    "max_depth": int | None,    # 3 a 30 ou None
    "min_samples_split": int,   # 2 a 20
    "min_samples_leaf": int,    # 1 a 10
    "max_features": str,        # "sqrt", "log2", None
    "class_weight": str | None  # "balanced", "balanced_subsample", None
}
```

Para Regressao Logistica:

```python
{
    "C": float,                 # 0.001 a 100
    "penalty": str,             # "l1", "l2"
    "solver": str,              # "liblinear", "saga"
    "class_weight": str | None, # "balanced" ou None
    "max_iter": int             # 500 a 3000
}
```

Para KNN:

```python
{
    "n_neighbors": int,         # 3 a 31, preferencialmente impar
    "weights": str,             # "uniform", "distance"
    "metric": str               # "euclidean", "manhattan", "minkowski"
}
```

Representacao recomendada:

- Usar dicionario tipado por modelo.
- Cada gene tem dominio e funcao de reparo.
- Crossover deve respeitar dominios.
- Mutacao deve trocar valores dentro do dominio.

### 6.3 Inicializacao da Populacao

Combinar:

- Inicializacao aleatoria para diversidade.
- Hotstart com hiperparametros baseline da Fase 1.
- Hotstart com boas configuracoes conhecidas, por exemplo Random Forest com `class_weight='balanced'`.

Isso aplica o conceito de hotstart das aulas: iniciar a populacao com solucoes informadas para acelerar convergencia.

### 6.4 Selecao

Opcoes recomendadas:

- Torneio: simples, robusto e facil de explicar.
- Roleta ponderada pelo fitness: coerente com o material de aula.
- Elitismo: copiar os melhores individuos para a proxima geracao.

Sugestao:

```text
elitismo = top 10% da populacao
selecao = torneio com k=3
```

### 6.5 Crossover

Como a codificacao e hibrida/discreta, usar crossover uniforme por gene:

```text
filho[gene] = gene do pai A ou pai B com probabilidade 50/50
```

Para genes numericos continuos, opcional:

```text
filho = alpha * pai_a + (1 - alpha) * pai_b
```

Mas para simplicidade academica, crossover uniforme e suficiente.

### 6.6 Mutacao

Mutacao por gene:

- Com probabilidade `taxa_mutacao`, sortear novo valor dentro do dominio.
- Para inteiros, somar ruido pequeno e aplicar limites.
- Para categoricos, trocar por outra categoria.
- Para floats como `C`, mutar em escala logaritmica.

### 6.7 Condicao de Parada

Usar pelo menos uma:

- Numero maximo de geracoes.
- Estagnacao: sem melhora apos N geracoes.
- Fitness alvo.

Recomendacao:

```text
max_geracoes = 20 a 50
patience = 8
```

### 6.8 Experimentos Obrigatorios

O enunciado pede ao menos 3 experimentos com configuracoes diferentes. Proposta:

| Experimento | Populacao | Geracoes | Mutacao | Crossover | Objetivo |
|---|---:|---:|---:|---:|---|
| GA-Exploratorio | 20 | 20 | 0.25 | 0.80 | Explorar muito o espaco |
| GA-Balanceado | 30 | 30 | 0.15 | 0.75 | Equilibrar busca e custo |
| GA-Conservador | 20 | 40 | 0.08 | 0.65 | Refinar boas solucoes |

Registrar para cada experimento:

- melhor individuo;
- melhor fitness;
- recall/F1/AUC/accuracy em validacao;
- metricas no teste final;
- tempo total;
- curva de convergencia;
- diversidade media da populacao.

## 7. Integracao com LLM

### 7.1 O que as Aulas Ensinam

Das aulas de LLMs e IA Generativa:

- LLMs sao baseados em Transformers.
- Transformers usam autoatencao para capturar contexto global.
- Embeddings representam tokens em vetores com informacao semantica.
- LLMs podem gerar linguagem natural, resumo, traducao, classificacao, chatbots e assistentes.
- Integracao pode ser feita de tres formas:
  - local/on-premises;
  - nuvem;
  - API de modelo pre-treinado.
- Devido ao custo de treinar LLMs, usar API ou modelo pre-treinado e o caminho mais viavel.
- RAG combina LLM com fontes confiaveis recuperadas.
- Prompt engineering influencia fortemente qualidade da resposta.
- Riscos: alucinacao, vies, privacidade, prompt injection, direitos autorais e falta de verificabilidade.

### 7.2 Uso da LLM no Challenge

Usar a LLM para explicar, nao para diagnosticar diretamente.

Entradas possiveis:

- Metricas globais dos modelos.
- Comparacao baseline vs otimizado.
- Top features do Random Forest.
- SHAP values de paciente individual.
- Probabilidade prevista.
- Classe prevista.
- Ressalvas clinicas.

Saidas esperadas:

- Explicacao para medico.
- Resumo tecnico para equipe de dados.
- Alertas sobre limitacoes do modelo.
- Recomendacoes de proxima investigacao clinica sem prescrever tratamento.

### 7.3 Prompt Base Recomendado

```text
Voce e um assistente de apoio a interpretacao de modelos de machine learning em saude.
Nao forneca diagnostico definitivo, prescricao ou conduta medica.
Explique os resultados como apoio a triagem clinica.

Contexto:
- Doenca-alvo: Sindrome dos Ovarios Policisticos (SOP).
- Modelo: {modelo}.
- Classe positiva: paciente com SOP.
- Probabilidade prevista: {probabilidade_sop}.
- Resultado previsto: {classe_prevista}.
- Principais fatores do caso: {top_features_paciente}.
- Metricas globais do modelo: {metricas_modelo}.

Tarefa:
1. Explique em linguagem natural por que o modelo sugeriu esse resultado.
2. Destaque os fatores que mais contribuiram.
3. Informe o nivel de cautela com base nas metricas.
4. Liste limitacoes do modelo.
5. Termine reforcando que a decisao final e medica.

Formato:
- Resumo clinico em ate 5 linhas.
- Fatores principais em bullets.
- Limitacoes em bullets.
- Recomendacao de uso seguro.
```

### 7.4 Avaliacao das Interpretacoes

Criar uma rubrica simples com notas de 1 a 5:

- Fidelidade aos dados: nao inventa informacoes.
- Clareza: compreensivel para profissional de saude.
- Utilidade: transforma numeros em insights acionaveis.
- Cautela medica: nao substitui medico nem prescreve.
- Completude: inclui fatores, incerteza e limitacoes.

Tambem validar automaticamente:

- Se a resposta menciona que e apoio a triagem.
- Se nao usa termos proibidos como "diagnostico definitivo".
- Se nao recomenda medicamento ou tratamento.
- Se cita as principais features recebidas no prompt.

### 7.5 RAG Opcional

RAG pode melhorar a resposta usando documentos confiaveis:

- README/relatorio da Fase 1.
- Secao de limitacoes do projeto.
- Pequeno glossario de SOP.
- Criterios clinicos de features usadas, sem extrapolar para recomendacao medica.

Fluxo:

```text
pergunta ou caso -> recuperar contexto relevante -> montar prompt enriquecido -> LLM -> avaliacao da resposta
```

## 8. Monitoramento, Logging e Escalabilidade

### 8.1 Requisito do Enunciado

O enunciado pede configurar recursos de escalabilidade automatica e implementar monitoramento/logging. A observacao diz que nuvem e opcional e vale como extra.

Como implementacao local suficiente:

- Logs estruturados em JSONL.
- Registro de cada individuo avaliado.
- Registro de cada geracao.
- Registro de tempo de treinamento por modelo.
- Registro das metricas finais.
- Graficos de convergencia.
- Arquivo `experiments.csv` ou `experiments.json`.

### 8.2 Design Preparado para Cloud

Mesmo sem implantar em nuvem, documentar arquitetura cloud-ready:

```text
API/CLI -> fila de experimentos -> workers de treinamento -> storage de artefatos -> dashboard/logs
```

Possiveis servicos por provedor:

- Azure ML: compute clusters, hyperparameter tuning, AutoML.
- Google Cloud: Vertex AI, Cloud Run, Cloud Storage.
- AWS: SageMaker, S3, CloudWatch.

Autoescalabilidade opcional:

- Worker containerizado.
- Cada experimento como job independente.
- Escala horizontal por quantidade de experimentos pendentes.
- Persistencia de resultados em storage.

## 9. Testes Automatizados Recomendados

### Algoritmo Genetico

- Cromossomos gerados sempre respeitam dominio.
- Crossover gera filhos validos.
- Mutacao mantem valores validos.
- Fitness retorna numero finito.
- Elitismo preserva melhor individuo.
- Otimizador melhora ou mantem melhor fitness ao longo das geracoes.

### Pipeline ML

- Loader encontra os arquivos.
- Pre-processamento remove ausentes.
- Split e estratificado.
- Normalizador e ajustado apenas no treino.
- Modelo treina e retorna metricas esperadas.

### LLM

- Prompt contem dados obrigatorios.
- Prompt inclui regra de nao diagnostico definitivo.
- Avaliador identifica respostas inseguras.
- Provider tem fallback/mock para testes sem API real.

## 10. Relatorio Tecnico Esperado

Estrutura recomendada:

1. Introducao
   - Continuidade da Fase 1.
   - Problema medico e motivacao.
   - Objetivo da Fase 2.

2. Dataset e baseline
   - Fonte dos dados.
   - Pipeline herdado.
   - Modelos da Fase 1.
   - Metricas baseline.

3. Algoritmo genetico
   - Representacao dos genes.
   - Populacao inicial e hotstart.
   - Fitness.
   - Selecao.
   - Crossover.
   - Mutacao.
   - Elitismo e parada.

4. Experimentos
   - Configuracao dos 3 experimentos.
   - Tabelas de resultados.
   - Curvas de convergencia.
   - Analise de custo computacional.

5. Comparativo baseline vs otimizado
   - Accuracy, recall, F1, AUC.
   - Matriz de confusao.
   - Discussao de falso negativo.

6. LLM e interpretabilidade
   - Modelo/API escolhido.
   - Prompts.
   - Exemplos de resposta.
   - Avaliacao de qualidade.
   - Limites e riscos.

7. Monitoramento e arquitetura
   - Logs.
   - Tracking.
   - Arquitetura local.
   - Arquitetura cloud opcional.

8. Limitacoes
   - Dataset pequeno.
   - Origem geografica restrita.
   - Dados historicos.
   - Risco de vies.
   - LLM pode alucinar.
   - Nao e diagnostico definitivo.

9. Conclusao
   - Ganhos obtidos.
   - Melhor modelo.
   - Uso seguro como triagem.
   - Proximos passos.

## 11. Roteiro do Video de Demonstracao

Tempo maximo: 15 minutos.

Sugestao:

1. 0:00-1:30 - Contexto: Fase 1 e objetivo da Fase 2.
2. 1:30-3:00 - Dataset e baseline.
3. 3:00-6:00 - Como o algoritmo genetico funciona no projeto.
4. 6:00-8:30 - Resultados dos 3 experimentos.
5. 8:30-10:30 - Comparativo baseline vs otimizado.
6. 10:30-13:00 - Demo da LLM explicando um caso.
7. 13:00-14:30 - Monitoramento/logs/arquitetura.
8. 14:30-15:00 - Limitacoes e conclusao.

## 12. Conteudo das Aulas Aplicado ao Challenge

### Processamento de Linguagem Natural

- Aula 1: fundamentos de PLN, niveis morfologico/sintatico/semantico, aplicacoes como chatbots, busca, analise de sentimento e resumo.
- Aula 2: Bag of Words, WordCloud e classificacao de sentimento com regressao logistica.
- Aula 3: tokenizacao com NLTK, remocao de stopwords, pontuacao, acentos e normalizacao.
- Aula 4: stemming, TF-IDF e N-grams; reducao de dimensionalidade e pesos de termos.
- Aula 5: Word Embeddings com Word2Vec, CBOW e Skip-Gram; representacao semantica.
- Aula 6: spaCy para tokenizacao, morfologia, sintaxe, entidades, vetores e classificacao.

Aplicacao no Projeto 1:

- Usar conceitos de NLP para estruturar prompts, avaliar respostas e preparar futuro uso de dados textuais.
- Opcionalmente, criar um glossario ou pequeno corpus para RAG.
- Aplicar tokenizacao/embeddings se for implementado um buscador de contexto local.

### Introducao ao Algoritmo Genetico

- Aula 1: otimizacao, solucoes exatas vs heuristicas, TSP, vizinho mais proximo e custo computacional.
- Aula 2: inspiracao biologica, evolucao, neuroevolucao e NEAT.
- Aula 3: codificacao binaria/real/combinatoria/hibrida, inicializacao, fitness, crossover, mutacao, populacao, convergencia e diversidade.
- Aula 4: implementacao de fitness, selecao, matriz de distancias, hotstart e eficiencia computacional.
- Aula 5: operadores geneticos, crossover OX1, mutacoes, benchmark e visualizacao.

Aplicacao no Projeto 1:

- Usar codificacao hibrida para hiperparametros.
- Usar fitness composto por metricas medicas.
- Usar selecao, crossover, mutacao e elitismo.
- Rodar 3 experimentos e discutir exploracao vs aproveitamento.

### Desenvolvimento de ML na Cloud

- Aula 1: etapas de ML, coleta, pre-processamento, treinamento, avaliacao, implantacao e monitoramento; servicos cognitivos.
- Aula 2: plataformas e recursos para ML, datasets, compute, serverless e servicos gerenciados.
- Aula 3: AutoML, hyperparameter tuning, paralelismo, CPU/GPU/TPU, grid search, random search, otimizacao bayesiana e algoritmos evolutivos.

Aplicacao no Projeto 1:

- Documentar pipeline completo.
- Registrar experimentos.
- Preparar arquitetura cloud-ready.
- Relacionar AG a hyperparameter tuning evolutivo.
- Tratar cloud como opcional/extra.

### Desvendando o Poder das LLMs

- Aula 1: evolucao dos LLMs, teste de Turing, chatbots iniciais, Word Embeddings, Transformers, alucinacao e desafios eticos.
- Aula 2: Transformers, atencao multi-cabeca, BERT/GPT, treinamento supervisionado/nao supervisionado, custo computacional, alucinacao, vies, RAG e interpretabilidade.
- Aula 3: LLMs em traducao, in-context learning, templates, exemplos no prompt, BLEU/COMET e avaliacao.
- Aula 4: chatbots e assistentes virtuais, contexto conversacional, fine-tuning, prompt engineering e RAG.
- Aula 5: integracao pratica com LLMs, execucao local, nuvem ou APIs, custo de operacao, limite de VRAM e uso viavel de APIs pre-treinadas.

Aplicacao no Projeto 1:

- Usar LLM via API ou modelo pre-treinado.
- Projetar prompt com contexto, papel, tarefa e formato.
- Evitar que a LLM invente diagnostico.
- Avaliar qualidade das respostas.
- Justificar uso de API pelo custo proibitivo de treinar LLM.

### IA Generativa

- Aula 1: conceito de IA generativa, deep learning, GANs, LLMs, Transformers e aplicacoes empresariais.
- Aula 2: fundamentos de redes neurais, CNNs, RNNs, tokenizacao, embeddings e contexto.
- Aula 3: geracao de imagens, videos e codigo; importancia de prompt engineering.
- Aula 4: projeto pratico com Gemini e RAG; embeddings e recuperacao de informacao.
- Aula 5: desafios eticos, privacidade, seguranca, prompt injection, direitos autorais, fake news e vies.

Aplicacao no Projeto 1:

- LLM deve ser usada de forma responsavel.
- Dados sensiveis nao devem ser enviados sem anonimizar.
- Prompt deve conter barreiras de seguranca.
- Explicacoes devem ter disclaimers clinicos.
- Avaliacao deve checar alucinacao, vies e extrapolacao.

## 13. Riscos e Decisoes Criticas

### Risco 1: Escopo grande demais

Mitigacao:

- Focar Projeto 1.
- Otimizar dois modelos no maximo.
- LLM para explicacao, nao chatbot completo.
- Cloud apenas documentada, se o prazo apertar.

### Risco 2: LLM gerar informacao medica indevida

Mitigacao:

- Prompt com restricoes.
- Rubrica de avaliacao.
- Nao recomendar tratamento.
- Sempre afirmar que e apoio a triagem.

### Risco 3: AG ficar lento

Mitigacao:

- Usar validacao simples no fitness.
- Limitar populacao e geracoes.
- Cachear avaliacoes de cromossomos repetidos.
- Paralelizar opcionalmente.

### Risco 4: Otimizacao piorar recall

Mitigacao:

- Fitness prioriza recall.
- Comparar metricas completas.
- Escolher melhor modelo pelo objetivo clinico, nao apenas accuracy.

### Risco 5: Reprodutibilidade

Mitigacao:

- `random_state=42`.
- Salvar config dos experimentos.
- Salvar versoes de dependencias.
- Salvar resultados em arquivos.

## 14. Definicao de Pronto

O challenge estara pronto quando houver:

- Pipeline da Fase 1 reproduzido.
- Baselines recalculados.
- Algoritmo genetico implementado sem bibliotecas magicas escondendo a logica principal.
- Pelo menos 3 experimentos de AG.
- Comparativo baseline vs otimizado.
- Logs e tracking de experimentos.
- LLM integrada para explicacoes.
- Avaliacao das explicacoes.
- Testes automatizados.
- README com setup e execucao.
- Relatorio tecnico.
- Notebook ou script de demonstracao.
- Roteiro de video.

## 15. Prompt para Futuras Sessoes de IA

Use este bloco para iniciar uma nova sessao de desenvolvimento:

```text
Estamos desenvolvendo o Tech Challenge Fase 2 da FIAP POSTECH IA para Devs.
Escolhemos o Projeto 1: otimizar os modelos de diagnostico de SOP da Fase 1 com algoritmos geneticos e integrar LLM para interpretacao dos resultados.

Contexto da Fase 1:
- Dataset PCOS Kaggle, 541 pacientes.
- Target: PCOS (Y/N).
- Modelos baseline: Regressao Logistica, Arvore de Decisao, Random Forest e KNN.
- Recall da classe positiva e a metrica mais importante.
- Feature engineering existente: total_foliculos, soma_sintomas, faixa_imc, razao_lh_fsh.

Objetivos da Fase 2:
- Implementar algoritmo genetico para otimizar hiperparametros.
- Realizar pelo menos 3 experimentos variando populacao, mutacao e crossover.
- Comparar baseline vs modelo otimizado.
- Implementar logging/monitoramento local.
- Integrar LLM para explicacoes em linguagem natural, com prompt seguro e avaliacao de qualidade.
- Criar testes, README, relatorio tecnico e demo.

Restricoes:
- Nao substituir decisao medica.
- Nao gerar recomendacao de tratamento.
- Preservar reprodutibilidade.
- Codigo simples, didatico e bem documentado.
```

## 16. Fontes Lidas

Enunciado e projeto:

- `IADT - Fase 2 - Tech challenge.pdf`
- `Capítulo de Projeto - 4IADT - Fase 2.pdf`

Aulas:

- `POSTECH - Processamento de Linguagem Natural - Aula 1.pdf`
- `POSTECH - Processamento de Linguagem Natural - Aula 2.pdf`
- `POSTECH - Processamento de Linguagem Natural - Aula 3.pdf`
- `POSTECH - Processamento de Linguagem Natural - Aula 4.pdf`
- `POSTECH - Processamento de Linguagem Natural - Aula 5.pdf`
- `POSTECH - Processamento de Linguagem Natural - Aula 6.pdf`
- `POSTECH - Introducao Algoritmo Genetico - Aula 1.pdf`
- `POSTECH - Introducao Algoritmo Genetico - Aula 2.pdf`
- `POSTECH - Introducao Algoritmo Genetico - Aula 3.pdf`
- `POSTECH - Introducao Algoritmo Genetico - Aula 4.pdf`
- `POSTECH - Introducao Algoritmo Genetico - Aula 5.pdf`
- `POSTECH - Desenvolvimento de ML na cloud - Aula 1.pdf`
- `POSTECH - Desenvolvimento de ML na cloud - Aula 2.pdf`
- `POSTECH - Desenvolvimento de ML na cloud - Aula 3.pdf`
- `POSTECH - Desvendando o poder das LLMs - Aula 1.pdf`
- `POSTECH - Desvendando o poder das LLMs - Aula 2.pdf`
- `POSTECH - Desvendando o poder das LLMs - Aula 3.pdf`
- `POSTECH - Desvendando o poder das LLMs - Aula 4.pdf`
- `POSTECH - Desvendando o poder das LLMs - Aula 5.pdf`
- `POSTECH - Aula 1 - Introdução a IA Generativa.pdf`
- `POSTECH - Aula 2 - Fundamentos da IA Generativa.pdf`
- `POSTECH - Aula 3 - O uso de IAs Generativas na geração de códigos^J imagens e vídeos.pdf`
- `POSTECH - Aula 4 - Projetos Práticos com a IA generativa.pdf`
- `POSTECH - Aula 5 - Os desafios éticos das IAs Generativas na criação de conteúdo.pdf`
