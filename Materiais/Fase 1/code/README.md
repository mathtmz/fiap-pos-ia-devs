# Diagnóstico de SOP com Machine Learning — Tech Challenge Fase 1

**FIAP POSTECH — IA para Devs**

Sistema de apoio ao diagnóstico de **Síndrome dos Ovários Policísticos (SOP)** usando Machine Learning aplicado a dados clínicos de 541 pacientes coletados em 10 hospitais de Kerala, Índia.

---

## Resultados obtidos

| Modelo               | Acurácia | Recall  | F1-Score | AUC-ROC |
|----------------------|----------|---------|----------|---------|
| Regressão Logística  | 88.99%   | **88.89%** | 84.21%   | 0.9513  |
| Árvore de Decisão    | 86.24%   | 83.33%  | 80.00%   | 0.8950  |
| Random Forest        | 90.83%   | 80.56%  | **85.29%** | 0.9351  |

> **Recall** é a métrica prioritária: um falso negativo (paciente com SOP classificada como saudável) tem consequências clínicas graves.

---

## Estrutura do projeto

```
code/
├── pcos_diagnostico.ipynb           # Notebook principal (limpo, para submissão)
├── pcos_diagnostico_executado.ipynb # Notebook com todas as células executadas e outputs
├── graficos/                        # 12 gráficos gerados automaticamente
│   ├── 01_distribuicao_target.png
│   ├── 02_distribuicao_features_clinicas.png
│   ├── 03_boxplots_features.png
│   ├── 04_prevalencia_sintomas.png
│   ├── 05_correlacao_com_target.png
│   ├── 06_heatmap_correlacao.png
│   ├── 07_matrizes_confusao.png
│   ├── 08_curvas_roc.png
│   ├── 09_feature_importance.png
│   ├── 10_shap_summary.png
│   ├── 11_shap_bar.png
│   └── 12_shap_waterfall.png
└── README.md

pcos_data/
├── PCOS_data_without_infertility.xlsx  # Dataset principal
├── PCOS_infertility.csv                # Dataset complementar
└── venv/                               # Ambiente virtual Python
```

---

## Dataset

- **Fonte:** [Kaggle — Polycystic Ovary Syndrome (PCOS)](https://www.kaggle.com/datasets/prasoonkottarathil/polycystic-ovary-syndrome-pcos)
- **Citação:** Prasoon Kottarathil, 2020
- **Tamanho:** 541 pacientes × 44 features clínicas
- **Target:** `PCOS (Y/N)` — 0 = sem SOP (364 pacientes), 1 = com SOP (177 pacientes)

---

## Como executar

### Pré-requisitos

```bash
# Na raiz do projeto (Fase 1/)
cd pcos_data
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy scikit-learn matplotlib seaborn shap jupyter openpyxl nbformat
```

### Executar o notebook

```bash
cd code
source ../pcos_data/venv/bin/activate
jupyter notebook pcos_diagnostico.ipynb
```

Ou para executar e gerar o notebook com outputs:

```bash
jupyter nbconvert --to notebook --execute pcos_diagnostico.ipynb \
  --output pcos_diagnostico_executado.ipynb
```

---

## Fluxo do notebook

1. **Importação** — bibliotecas e constante `SEMENTE_ALEATORIA = 42`
2. **Carregamento** — leitura do Excel + CSV, merge pelo `Patient File No.`, remoção de colunas irrelevantes e limpeza de valores inválidos
3. **EDA** — distribuição do target, histogramas e boxplots por grupo, prevalência de sintomas clínicos
4. **Pré-processamento** — imputação com mediana, encoding de categóricas (LabelEncoder), análise de correlação (heatmap), divisão 80/20 com stratify, normalização com StandardScaler (fit apenas no treino)
5. **Modelos** — Regressão Logística, Árvore de Decisão, Random Forest com `class_weight='balanced'`
6. **Avaliação** — classification report, matrizes de confusão, curvas ROC/AUC, validação cruzada K-Fold (k=5)
7. **Explicabilidade** — Feature Importance (Random Forest), SHAP summary plot, SHAP bar plot, SHAP waterfall para previsão individual
8. **Conclusão** — discussão crítica sobre aplicabilidade prática e limitações
