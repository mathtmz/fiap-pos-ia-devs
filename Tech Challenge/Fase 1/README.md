# Tech Challenge — Fase 1: Diagnóstico de SOP com Machine Learning

**FIAP POSTECH — IA para Devs | Fase 1**

Sistema de apoio ao diagnóstico de **Síndrome dos Ovários Policísticos (SOP)** usando Machine Learning aplicado a dados clínicos de 541 pacientes coletados em 10 hospitais de Kerala, Índia.

---

## Resultados obtidos

| Modelo               | Acurácia | Recall      | F1-Score    | AUC-ROC |
|----------------------|----------|-------------|-------------|---------|
| Regressão Logística  | 89.91%   | **88.89%**  | 85.33%      | 0.9631  |
| Árvore de Decisão    | 86.24%   | 80.56%      | 79.45%      | 0.8701  |
| Random Forest        | **93.58%**| 83.33%     | **89.55%**  | 0.9505  |
| KNN (k=5)            | 90.83%   | 77.78%      | 84.85%      | 0.9614  |

> **Recall** é a métrica prioritária: um falso negativo (paciente com SOP não diagnosticada) tem consequências clínicas graves.

---

## Estrutura do projeto

```
Tech Challenge/Fase 1/
│
├── README.md                               ← este arquivo
├── IADT - Fase 1 - Tech challenge A.pdf    ← enunciado do challenge
│
├── code/
│   ├── pcos_diagnostico.ipynb              ← notebook principal (limpo)
│   ├── pcos_diagnostico_executado.ipynb    ← notebook com todos os outputs
│   └── graficos/                           ← 14 gráficos gerados
│       ├── 01_distribuicao_target.png
│       ├── 02_distribuicao_features_clinicas.png
│       ├── 03_boxplots_features.png
│       ├── 04_prevalencia_sintomas.png
│       ├── 05_correlacao_com_target.png
│       ├── 05_heatmap_correlacao.png
│       ├── 07_matrizes_confusao.png
│       ├── 08_curvas_roc.png
│       ├── 09_feature_importance.png
│       ├── 10_shap_summary.png
│       ├── 11_shap_bar.png
│       ├── 12_shap_waterfall.png
│       └── fe_01_novas_features.png
│
└── data/
    ├── PCOS_data_without_infertility.xlsx  ← dataset principal (541 × 44)
    └── PCOS_infertility.csv                ← dataset complementar
```

---

## Dataset

- **Fonte:** [Kaggle — Polycystic Ovary Syndrome (PCOS)](https://www.kaggle.com/datasets/prasoonkottarathil/polycystic-ovary-syndrome-pcos)
- **Citação:** Prasoon Kottarathil, 2020 — 10 hospitais do estado de Kerala, Índia
- **Tamanho:** 541 pacientes × 44 variáveis clínicas
- **Target:** `PCOS (Y/N)` — 0 = sem SOP (364), 1 = com SOP (177)

---

## Como executar

### 1. Criar e ativar o ambiente virtual

```bash
cd "Tech Challenge/Fase 1"
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# ou
venv\Scripts\activate             # Windows
```

### 2. Instalar as dependências

```bash
pip install pandas numpy scikit-learn matplotlib seaborn shap jupyter openpyxl nbformat
```

### 3. Executar o notebook

```bash
cd code
jupyter notebook pcos_diagnostico.ipynb
```

Ou para executar automaticamente e gerar o notebook com todos os outputs:

```bash
jupyter nbconvert --to notebook --execute pcos_diagnostico.ipynb \
  --output pcos_diagnostico_executado.ipynb
```

---

## Fluxo do notebook

| Seção | Conteúdo |
|---|---|
| 1. Imports | Bibliotecas: pandas, numpy, sklearn, seaborn, shap |
| 2. Carregamento | Leitura do Excel + CSV, merge, remoção de colunas irrelevantes |
| 3. EDA | Distribuição do target, histogramas, boxplots, prevalência de sintomas |
| 4. Pré-processamento | Imputação com mediana, LabelEncoder, StandardScaler (fit só no treino) |
| 5. Feature Engineering | 4 features derivadas + feature selection por correlação (31 de 45 retidas) |
| 6. Modelagem | Regressão Logística, Árvore de Decisão, Random Forest, KNN |
| 7. Avaliação | Classification report, matrizes de confusão, curvas ROC/AUC, K-Fold |
| 8. Explicabilidade | Feature Importance + SHAP (summary, bar, waterfall) |
| 9. Resumo | Tabela comparativa dos 4 modelos |
| 10. Conclusão | Discussão crítica, limitações, próximos passos |

---

## Feature Engineering

Criamos 4 features derivadas com base em conhecimento clínico e nos padrões observados na EDA:

| Feature | Lógica | Correlação c/ SOP | Importância RF |
|---|---|---|---|
| `total_foliculos` | Follicle L + Follicle R | **+0.660** | **#1 (18.2%)** |
| `soma_sintomas` | Soma de 5 sintomas binários | **+0.580** | **#3 (10.3%)** |
| `faixa_imc` | BMI categorizado (faixas OMS) | +0.165 | #29 |
| `razao_lh_fsh` | LH / FSH | +0.065 | #12 |

---

## Técnicas aplicadas (mapeamento com as aulas)

| Técnica | Aula de referência |
|---|---|
| Aprendizado supervisionado de classificação | ML Aula 1 |
| Correlação e análise de relação entre variáveis | ML Aula 2 |
| Feature Engineering e PCA | ML Aula 3 |
| StandardScaler / MinMaxScaler | ML Aula 4 |
| LabelEncoder, One Hot Encoding | MLA Aula 1 |
| KNN com busca do melhor k | MLA Aula 2 |
| Árvore de Decisão, Random Forest | MLA Aula 4 |
| Validação Cruzada K-Fold | MLA Aula 5 |
| Matriz de confusão, Recall, F1, classification_report | MLA Aula 6 |
| Curva ROC e AUC | MLA Aula 7 |
| SHAP Values | MLA Aulas 6/7 |

---

## Discussão crítica

O **Random Forest** teve o melhor F1 (89.55%) e a **Regressão Logística** teve o maior Recall (88.89%) — preferível para triagem médica, onde errar para o lado da cautela é menos grave.

O modelo pode ser utilizado como ferramenta de **apoio à triagem**, acelerando o diagnóstico em unidades de saúde com alto volume de pacientes. **O médico sempre tem a palavra final.**

### Limitações

- Dataset pequeno (541 pacientes) — ideal seria dezenas de milhares
- Origem geográfica restrita (Kerala, Índia)
- Dados de ultrassom dependem do equipamento e do operador
- Não testado prospectivamente em ambiente clínico real
