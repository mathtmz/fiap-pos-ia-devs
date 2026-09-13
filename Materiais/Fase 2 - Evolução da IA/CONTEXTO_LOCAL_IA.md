# Contexto local para IA - Tech Challenge Fase 2

Este arquivo e local e nao deve ser enviado ao GitHub. Ele serve para orientar futuras sessoes de IA sobre o projeto, o contexto das aulas e as decisoes ja tomadas.

## Projeto

- Curso: FIAP POSTECH - IA para Devs.
- Fase: 2 - Evolucao da IA.
- Projeto escolhido: Projeto 1, otimizacao de modelos de diagnostico.
- Tema: diagnostico assistido de Sindrome dos Ovarios Policisticos (SOP/PCOS).
- Base: evolucao direta da Fase 1.

## Leitura correta do Tech Challenge

O enunciado pede:

1. Algoritmo genetico para otimizacao de hiperparametros.
2. Recursos de escalabilidade automatica para lidar com variacoes de demanda.
3. Monitoramento e logging para tracking de desempenho.
4. Documentacao de arquitetura e decisoes.
5. Integracao com LLM para interpretacao de resultados.

A interpretacao final adotada para o item 2:

- escalabilidade nao deve ser narrada como API HTTP;
- o foco e escalar treinamentos, testes e experimentos de otimizacao;
- cada configuracao do algoritmo genetico pode ser entendida como um job;
- o numero de workers usados na grade de jobs e definido automaticamente (CPU disponivel x jobs pendentes), nao por um valor fixo escolhido manualmente;
- os logs e metricas servem para comparar execucoes e escolher o melhor modelo.

Essa leitura foi revisada apos conferir o material de referencia da disciplina (`lucolivi/ml-cloud-materiais`): la, "escalabilidade" aparece como compute cluster + sweep jobs (jobs de treinamento em paralelo, limitados por `max_concurrent_trials`), nunca como serving. Isso confirma a leitura acima, mas exige que o dimensionamento de workers seja automatico, nao apenas paralelo com um numero fixo passado por linha de comando.

## Referencia das aulas de ML na Cloud

Repositorio consultado: `https://github.com/lucolivi/ml-cloud-materiais`.

Pontos relevantes:

- Aula 2 mostra scripts parametrizaveis de treinamento com `argparse`.
- Os exemplos usam tracking de metricas e artefatos, inclusive com MLflow.
- Aula 3 aborda hyperparameter tuning, AutoML e execucao de experimentos.
- Ha exemplos de treinamento distribuido e uso de jobs/workers.

Decisao do projeto (revisada):

- adicionar MLflow em modo local (backend em arquivo), complementando o tracking em JSON/JSONL/CSV ja existente, para ficar alinhado a ferramenta usada no material de referencia; o registro das execucoes nao depende de servidor, e `mlflow ui --backend-store-uri ./mlruns` pode ser usado localmente so para visualizacao;
- adicionar logging de aplicacao (modulo `logging` do Python) em `outputs/logs/pipeline.log`;
- dimensionar workers automaticamente na grade de jobs, com `--workers` como override manual opcional;
- manter toda a execucao local, sem qualquer integracao real de nuvem.

## Estrutura principal do codigo

- `src/pcos_fase2/data.py`: limpeza, feature engineering, split e escala.
- `src/pcos_fase2/models.py`: baselines e construcao de modelos.
- `src/pcos_fase2/genetic_optimizer.py`: algoritmo genetico principal.
- `src/pcos_fase2/advanced_tuning.py`: investigacao adicional de tuning e threshold.
- `src/pcos_fase2/evaluation.py`: metricas, fitness e avaliacao.
- `src/pcos_fase2/llm_explainer.py`: prompt, mock, OpenAI, Gemini, checagem de seguranca e avaliacao de qualidade.
- `src/pcos_fase2/scaling.py`: dimensionamento automatico de workers.
- `src/pcos_fase2/logging_setup.py`: configuracao do logging de aplicacao.
- `src/pcos_fase2/experiment_tracking.py`: tracking em arquivos e integracao com MLflow local.
- `scripts/run_baseline.py`: reproduz baselines.
- `scripts/run_ga_experiments.py`: executa os tres experimentos principais.
- `scripts/run_ga_job.py`: executa um job parametrizado de GA.
- `scripts/run_ga_experiment_grid.py`: executa uma grade de jobs em paralelo local.
- `scripts/summarize_experiment_grid.py`: consolida resultados de jobs.
- `scripts/run_advanced_tuning.py`: tuning adicional.
- `scripts/finalize_ga_results.py`: consolida resultados principais e gera artefatos.
- `scripts/generate_llm_report.py`: gera relatorio de explicacao com LLM.
- `scripts/run_full_pipeline.py`: roda o fluxo completo local.

## Resultados principais

Baselines:

- Random Forest baseline: accuracy 93.58%, recall SOP 83.33%, F1 SOP 89.55%, AUC 95.05%.
- Regressao Logistica: recall SOP 88.89%, F1 SOP 85.33%.

GA principal:

- melhor cromossomo em validacao:
  - `class_weight=None`
  - `max_depth=32`
  - `max_features=log2`
  - `min_samples_leaf=2`
  - `min_samples_split=6`
  - `n_estimators=200`
- no teste final, nao superou o Random Forest baseline.

Tuning adicional:

- Random Forest com threshold 0.60:
  - accuracy 94.50%
  - precision SOP 100.00%
  - recall SOP 83.33%
  - F1 SOP 90.91%

## LLM

Providers:

- `mock`: padrao para execucao local e testes.
- `openai`: provider real, exige chave.
- `gemini`: provider real, exige chave.

Houve execucao real com Gemini. O resultado ficou salvo em `outputs/reports/llm_explanation.md`.

A LLM deve explicar resultados, nao diagnosticar nem recomendar tratamento.

## Comandos importantes

```bash
cd "Tech Challenge/Fase 2/code"
python -m pytest tests
python scripts/run_baseline.py
python scripts/run_ga_experiments.py
python scripts/run_ga_job.py --name smoke --population-size 6 --generations 2 --mutation-rate 0.1 --crossover-rate 0.7
python scripts/run_ga_experiment_grid.py --quick
python scripts/summarize_experiment_grid.py
python scripts/run_advanced_tuning.py
python scripts/finalize_ga_results.py
LLM_PROVIDER=mock python scripts/generate_llm_report.py
mlflow ui --backend-store-uri ./mlruns
```

## Cuidados para futuras sessoes

- Nao reintroduzir API HTTP como resposta de escalabilidade.
- Se falar de escalabilidade, falar de jobs, experimentos, treinamento e tuning.
- Nao versionar chaves.
- Nao commitar este arquivo.
- Manter na raiz da Fase 2 apenas `README.md` e `RELATORIO_TECNICO.md`.
- Evitar linguagem que pareca gerada por IA nos documentos finais.
