# Plano de Implementacao - Fase 2 / Projeto 1

## Objetivo

Evoluir o projeto da Fase 1, que classifica risco de SOP com modelos supervisionados, incorporando os conteudos centrais da Fase 2:

- algoritmos geneticos para otimizacao;
- modelos generativos/LLMs para explicacao e suporte a decisao;
- organizacao de experimentos;
- preparacao para arquitetura cloud e MLOps;
- avaliacao tecnica clara, comparavel e reprodutivel.

## Escopo tecnico

O trabalho deve manter o problema original: apoiar o diagnostico de SOP a partir de dados clinicos e laboratoriais. A evolucao nao deve substituir avaliacao medica; deve produzir uma ferramenta de apoio com transparencia sobre metricas, variaveis relevantes e limitacoes.

## Estrutura alvo

Proposta de organizacao para a pasta `Tech Challenge/Fase 2`:

```text
Tech Challenge/Fase 2/
├── README.md
├── CONTEXTO_TECH_CHALLENGE_FASE2.md
├── PLANO_IMPLEMENTACAO_FASE2.md
├── RELATORIO_TECNICO.md
├── data/
├── code/
│   ├── pcos_diagnostico.ipynb
│   ├── pcos_diagnostico_executado.ipynb
│   ├── src/
│   │   ├── config.py
│   │   ├── data_loader.py
│   │   ├── preprocessing.py
│   │   ├── models.py
│   │   ├── genetic_optimizer.py
│   │   ├── evaluation.py
│   │   ├── explainability.py
│   │   └── llm_explainer.py
│   ├── outputs/
│   │   ├── models/
│   │   ├── metrics/
│   │   └── figures/
│   └── tests/
```

## Fase 0 - Preparacao

1. Preservar a copia da Fase 1 em `Tech Challenge/Fase 1`.
2. Trabalhar somente em `Tech Challenge/Fase 2`.
3. Validar que o notebook copiado ainda executa com os caminhos relativos corrigidos.
4. Registrar versoes de dependencias em `requirements.txt` ou equivalente.
5. Separar artefatos gerados em `code/outputs/`.

## Fase 1 - Modularizacao do Pipeline

Extrair do notebook da Fase 1 os blocos de codigo essenciais:

- carregamento dos arquivos `PCOS_data_without_infertility.xlsx` e `PCOS_infertility.csv`;
- normalizacao dos nomes de colunas;
- merge das bases;
- tratamento de valores ausentes;
- separacao entre features e alvo;
- split treino/teste estratificado;
- preprocessamento numerico;
- treino de Regressao Logistica e Random Forest;
- avaliacao por accuracy, precision, recall, F1, matriz de confusao e AUC-ROC.

Critério de aceite:

- reproduzir metricas proximas ao baseline da Fase 1;
- ter funcoes reutilizaveis pelo notebook e pelo algoritmo genetico;
- evitar duplicacao pesada de codigo no notebook.

## Fase 2 - Algoritmo Genetico

Implementar um otimizador genetico para hiperparametros.

### Cromossomos recomendados

Para Random Forest:

| Gene | Valores candidatos |
| --- | --- |
| `n_estimators` | 50, 100, 150, 200, 300, 500 |
| `max_depth` | None, 3, 5, 8, 12, 16, 24, 32 |
| `min_samples_split` | 2, 4, 6, 8, 10, 15, 20 |
| `min_samples_leaf` | 1, 2, 3, 4, 5, 8, 10 |
| `max_features` | sqrt, log2, None |
| `class_weight` | balanced, balanced_subsample, None |

Para Regressao Logistica:

| Gene | Valores candidatos |
| --- | --- |
| `C` | 0.001, 0.01, 0.1, 1.0, 10.0, 100.0 |
| `penalty` | l1, l2 |
| `solver` | liblinear, saga |
| `class_weight` | balanced, None |
| `max_iter` | 500, 1000, 2000, 3000 |

### Funcao de fitness

Priorizar desempenho clinicamente util, favorecendo recall da classe positiva de SOP sem ignorar F1 e AUC:

```text
fitness = 0.50 * recall_pos
        + 0.30 * f1_pos
        + 0.15 * auc_roc
        + 0.05 * accuracy
        - penalidade_overfit
```

A penalidade de overfit deve ser aplicada quando houver diferenca excessiva entre metricas de treino/validacao ou validacao/teste.

### Operadores geneticos

- selecao: torneio ou roleta ponderada por fitness;
- crossover: troca parcial de genes entre dois individuos;
- mutacao: troca aleatoria de genes dentro do espaco permitido;
- elitismo: preservacao dos melhores individuos por geracao;
- parada: numero maximo de geracoes ou estabilidade do melhor fitness.

## Fase 3 - Experimentos Obrigatorios

Executar pelo menos tres configuracoes do algoritmo genetico:

| Experimento | Populacao | Geracoes | Mutacao | Crossover | Elitismo |
| --- | ---: | ---: | ---: | ---: | ---: |
| GA-Exploratorio | 20 | 20 | 0.25 | 0.80 | 10% |
| GA-Balanceado | 30 | 30 | 0.15 | 0.75 | 10% |
| GA-Conservador | 20 | 40 | 0.08 | 0.65 | 10% |

Comparar:

- baseline Random Forest da Fase 1;
- baseline Regressao Logistica da Fase 1;
- melhor Random Forest otimizado por GA;
- melhor Regressao Logistica otimizada por GA, se implementada.

Graficos minimos:

- evolucao do melhor fitness por geracao;
- fitness medio por geracao;
- matriz de confusao do melhor modelo;
- curva ROC;
- ranking de importancia das variaveis.

## Fase 4 - Explicabilidade e LLM

Implementar uma camada de explicacao em duas etapas:

1. Explicabilidade tecnica:
   - feature importance do Random Forest;
   - permutation importance ou SHAP, se viavel;
   - probabilidade predita e classe final;
   - variaveis mais influentes no caso analisado.

2. Explicacao com LLM:
   - transformar os resultados tecnicos em uma explicacao clara para o usuario;
   - explicitar que o resultado e apoio a decisao, nao diagnostico medico definitivo;
   - gerar recomendações de proximos passos sem prescrever tratamento;
   - manter o prompt com contexto, metricas e restricoes de seguranca.

### Prompt-base

```text
Voce e um assistente de apoio clinico educacional. Explique o resultado de um modelo de risco de SOP com linguagem clara, sem afirmar diagnostico definitivo.

Dados do caso:
- probabilidade prevista: {probabilidade}
- classificacao do modelo: {classe}
- principais variaveis influentes: {variaveis}
- metricas do modelo: {metricas}

Regras:
- nao prescreva medicamentos;
- recomende avaliacao com profissional de saude;
- explique incertezas e limitacoes;
- diferencie risco estimado de diagnostico clinico.
```

### Avaliacao das explicacoes

Usar uma rubrica simples:

| Criterio | O que avaliar |
| --- | --- |
| Fidelidade | A explicacao respeita a saida real do modelo? |
| Clareza | Um usuario nao tecnico entende o texto? |
| Cautela | O texto evita diagnostico definitivo e prescricao? |
| Utilidade | O texto indica proximos passos adequados? |
| Completude | O texto menciona incertezas e variaveis relevantes? |

## Fase 5 - Arquitetura Cloud e MLOps

Mesmo que a entrega seja local, documentar uma arquitetura alvo:

- camada de dados: armazenamento dos datasets e versoes;
- camada de treino: job batch para executar experimentos;
- camada de tracking: salvar parametros, metricas, artefatos e graficos;
- camada de inferencia: API para receber dados clinicos e retornar risco;
- camada de LLM: endpoint separado para explicacao textual;
- camada de observabilidade: logs, metricas, drift e auditoria.

Artefatos recomendados:

- `outputs/metrics/experiments.csv`;
- `outputs/models/best_model.joblib`;
- `outputs/figures/fitness_evolution.png`;
- `outputs/figures/confusion_matrix.png`;
- `outputs/figures/roc_curve.png`;
- `outputs/figures/feature_importance.png`.

## Fase 6 - Testes e Qualidade

Testes minimos:

- carregamento dos dados;
- schema minimo esperado;
- preprocessamento sem valores ausentes criticos;
- fitness retorna valor numerico valido;
- mutacao preserva genes dentro dos valores permitidos;
- crossover produz individuos validos;
- avaliacao retorna todas as metricas esperadas.

Validacoes minimas:

- notebook executa do inicio ao fim;
- scripts executam por linha de comando;
- graficos e metricas sao gerados;
- resultados sao reprodutiveis com `random_state`.

## Fase 7 - Relatorio e Video

O relatorio tecnico da Fase 2 deve responder:

1. Qual problema foi resolvido?
2. Qual foi o baseline herdado da Fase 1?
3. Como o algoritmo genetico foi modelado?
4. Qual funcao de fitness foi usada e por que?
5. Quais experimentos foram executados?
6. O modelo otimizado melhorou em quais metricas?
7. Como o LLM foi usado?
8. Quais sao as limitacoes tecnicas, clinicas e eticas?
9. Como essa solucao poderia ser implantada em cloud?

O video deve demonstrar:

- problema e dataset;
- execucao ou resultados do pipeline;
- evolucao do algoritmo genetico;
- melhor modelo e metricas;
- exemplo de explicacao gerada por LLM;
- conclusao sobre ganhos e limitacoes.

## Definicao de Pronto

- [ ] Fase 1 preservada sem alteracoes.
- [ ] Fase 2 com codigo independente.
- [ ] Pipeline modularizado.
- [ ] Algoritmo genetico implementado.
- [ ] Pelo menos tres experimentos executados.
- [ ] Melhor modelo comparado com baseline.
- [ ] Graficos e metricas salvos em `outputs/`.
- [ ] Explicacao com LLM implementada ou simulada de forma documentada.
- [ ] Relatorio tecnico atualizado para a Fase 2.
- [ ] Notebook executado salvo.
- [ ] Projeto pronto para PR.
