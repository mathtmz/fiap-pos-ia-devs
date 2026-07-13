# Tech Challenge - Fase 2: Otimizacao Evolutiva e LLM para Diagnostico de SOP

Projeto da FIAP POSTECH - IA para Devs, desenvolvido como evolucao direta da Fase 1. A pasta da Fase 2 foi criada como copia isolada para preservar a entrega anterior e permitir uma implementacao mais estruturada.

## Projeto escolhido

**Projeto 1 - Algoritmos Geneticos e Modelos Generativos aplicados ao projeto da Fase 1.**

A solucao evolui o classificador de SOP da Fase 1 com:

- pipeline Python modular;
- algoritmo genetico para otimizacao de hiperparametros;
- comparacao contra baselines;
- explicabilidade por feature importance e permutation importance;
- explicacao em linguagem natural com LLM/mock seguro;
- logs e artefatos de experimento;
- documentacao de arquitetura cloud-ready.

## Como executar

Entre na pasta de codigo:

```bash
cd "Tech Challenge/Fase 2/code"
```

Instale as dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Reproduza os baselines:

```bash
python scripts/run_baseline.py
```

Execute os experimentos de algoritmo genetico:

```bash
python scripts/run_ga_experiments.py
```

Consolide resultados a partir dos logs JSONL:

```bash
python scripts/finalize_ga_results.py
```

Gere a explicacao em linguagem natural:

```bash
LLM_PROVIDER=mock python scripts/generate_llm_report.py
```

Execute os testes:

```bash
python -m pytest tests
```

## Resultados

Baselines reproduzidos:

| Modelo | Accuracy | Recall SOP | F1 SOP | AUC-ROC |
| --- | ---: | ---: | ---: | ---: |
| Regressao Logistica | 89.91% | 88.89% | 85.33% | 96.31% |
| Arvore de Decisao | 86.24% | 80.56% | 79.45% | 87.01% |
| Random Forest | 93.58% | 83.33% | 89.55% | 95.05% |
| KNN | 90.83% | 77.78% | 84.85% | 96.14% |

Melhor cromossomo encontrado na validacao do algoritmo genetico:

```json
{
  "class_weight": null,
  "max_depth": 32,
  "max_features": "log2",
  "min_samples_leaf": 2,
  "min_samples_split": 6,
  "n_estimators": 200
}
```

No teste final, o modelo otimizado atingiu accuracy de 92.66%, recall positivo de 83.33%, F1 positivo de 88.24% e AUC-ROC de 94.98%. O resultado nao supera o Random Forest baseline no teste, o que e uma discussao relevante para o relatorio: a busca evolutiva melhorou o desempenho em validacao, mas nao trouxe ganho real de generalizacao no conjunto de teste.

## Artefatos principais

- `code/outputs/metrics/baseline_metrics.csv`
- `code/outputs/metrics/ga_history.csv`
- `code/outputs/metrics/model_comparison.csv`
- `code/outputs/metrics/feature_importance.csv`
- `code/outputs/models/best_model.joblib`
- `code/outputs/figures/fitness_evolution.png`
- `code/outputs/figures/confusion_matrix.png`
- `code/outputs/figures/roc_curve.png`
- `code/outputs/figures/feature_importance.png`
- `code/outputs/reports/llm_explanation.md`

## Documentos

- `CONTEXTO_TECH_CHALLENGE_FASE2.md`: consolidado do enunciado e das aulas.
- `PLANO_IMPLEMENTACAO_FASE2.md`: plano tecnico da implementacao.
- `RELATORIO_TECNICO.md`: relatorio final da Fase 2.

## Checklist

- [x] Preservar a Fase 1 sem alteracoes.
- [x] Modularizar pipeline de dados e modelos.
- [x] Reproduzir baselines.
- [x] Implementar algoritmo genetico.
- [x] Executar tres experimentos.
- [x] Gerar graficos e metricas.
- [x] Implementar explicacao com LLM/mock.
- [x] Criar testes automatizados.
- [x] Atualizar relatorio tecnico.
