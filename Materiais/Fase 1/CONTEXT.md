# Tech Challenge — Fase 1: Sistema de IA para Saúde Feminina (PCOS)

## Workspace
Raiz do projeto: `/Users/matomaz/Projects/FIAP/Tech Challenge/Fase 1/`
Todo código produzido vai em: `./code/`
Dados brutos em: `./pcos_data/`

---

## Problema e objetivo

Trabalho **acadêmico** de pós-graduação FIAP POSTECH (IADT - IA para Devs).  
**Peso:** 90% da nota. Entrega obrigatória.  
**Contexto:** rede de hospitais focada na saúde da mulher precisa de um sistema de suporte ao diagnóstico baseado em ML.  
**Tarefa escolhida:** classificação binária de SOP (Síndrome dos Ovários Policísticos) — 0 = sem SOP, 1 = com SOP.

---

## Dataset

**Fonte:** [Kaggle - Polycystic Ovary Syndrome (PCOS)](https://www.kaggle.com/datasets/prasoonkottarathil/polycystic-ovary-syndrome-pcos)  
**Citação:** Prasoon Kottarathil, 2020. Coletado em 10 hospitais do Kerala, Índia.

**Arquivos:**
- `./pcos_data/PCOS_data_without_infertility.xlsx` — sheet `Full_new` → dataset principal (541 × 44)
- `./pcos_data/PCOS_infertility.csv` → 3 features adicionais (beta-HCG I, beta-HCG II, AMH) — merge pelo `Patient File No.`

**Target:** `PCOS (Y/N)` — binário → 364 negativo / 177 positivo (~67% / ~33%)

**Colunas a remover:** `Sl. No`, `Patient File No.`, `Unnamed: 44` (coluna vazia)

**Missing values:** quase nenhum — 2 colunas com 1 valor ausente cada (`Marraige Status (Yrs)`, `Fast food (Y/N)`)

**Grupos de features:**
| Categoria | Features |
|---|---|
| Demográficas | Age, Weight, Height, BMI, Blood Group |
| Hormonais | FSH, LH, FSH/LH, AMH, TSH, PRL, beta-HCG I e II |
| Metabólicas | RBS (glicose), Hb, BP Systolic/Diastolic, Pulse rate, RR |
| Sintomas clínicos | Weight gain, hair growth, Skin darkening, Hair loss, Pimples |
| Ultrassom | Follicle No. L/R, Avg F size L/R, Endometrium |
| Comportamental | Fast food, Reg. Exercise |
| Reprodutiva | Cycle, Cycle length, Marraige Status, Pregnant, No. of abortions |

---

## Regras de código (trabalho acadêmico)

> Todo código deve ser **simples, bem documentado e didático**. O avaliador precisa entender o raciocínio.

- Comentários em português explicando o **porquê** de cada decisão
- Células Markdown no Jupyter com contexto clínico/técnico em cada seção
- Nomes de variáveis descritivos: `dados_treino`, `modelo_arvore`, `metricas_resultado`
- **Sem lambdas** — usar loops e funções nomeadas
- **Sem abstrações desnecessárias** — código linear e direto
- `random_state=42` em todo lugar que aceitar, para reprodutibilidade

---

## TO DO obrigatório

### 1. Dados e justificativa
- [ ] Documentar escolha do dataset e problema a resolver

### 2. Exploração de dados (EDA)
- [ ] Carregar e fazer merge dos dois arquivos pelo `Patient File No.`
- [ ] Explorar shape, dtypes, head, describe
- [ ] Visualizar distribuição do target (desequilíbrio 67/33%)
- [ ] Histogramas e boxplots das features relevantes
- [ ] Identificar e discutir padrões clínicos (AMH, FSH/LH, folículos)

### 3. Pré-processamento
- [ ] Remover colunas irrelevantes
- [ ] Tratar 2 missing values
- [ ] Converter `Blood Group` e outras categóricas (LabelEncoder ou OHE)
- [ ] Normalização / padronização das features numéricas (StandardScaler — fit só no treino)
- [ ] Análise de correlação (heatmap)

### 4. Modelagem (mínimo 2 algoritmos)
- [ ] Separação treino/teste 80/20 com `random_state=42`
- [ ] Modelo 1: Regressão Logística
- [ ] Modelo 2: Árvore de Decisão
- [ ] Modelo 3 (recomendado): Random Forest

### 5. Treinamento e avaliação
- [ ] Treinar cada modelo no conjunto de treino
- [ ] Avaliar no conjunto de teste: accuracy, recall, F1-score, matriz de confusão
- [ ] Discutir por que **recall** é a métrica mais crítica neste contexto médico (falso negativo = paciente com SOP não diagnosticada)
- [ ] Feature importance (Random Forest / DecisionTree)
- [ ] SHAP values para explicabilidade
- [ ] Discussão crítica: o modelo pode ser usado na prática? Limitações?

### 6. Entregáveis
- [ ] Notebook Jupyter completo em `./code/`
- [ ] `README.md` com instruções de execução
- [ ] Link do dataset documentado

---

## Conceitos das aulas aplicados neste projeto

### Machine Learning (Aulas 1–4) — prof. Ana Raquel

| Aula | Tópico | Aplicação no projeto |
|---|---|---|
| 1 | Tipos de aprendizado, pipeline ML | Aprendizado supervisionado de classificação |
| 2 | Regressão linear, métricas (MSE/RMSE/R²) | Base para entender métricas de validação |
| 3 | Redução de dimensionalidade, PCA | Opcional: reduzir as 44 features se necessário |
| 4 | Feature Scaling (MinMaxScaler, StandardScaler) | **Obrigatório** no pré-processamento — usar `StandardScaler` (fit apenas no treino) |

### Machine Learning Avançado (Aulas 1–7) — prof. Ana Raquel

| Aula | Tópico | Aplicação no projeto |
|---|---|---|
| 1 | Modelos de classificação, Label Encoding, One Hot Encoding | Pré-processamento de `Blood Group` e variáveis categóricas |
| 2 | KNN, SVM | Modelos alternativos para comparação |
| 3 | K-Means, DBSCAN (não supervisionado) | Não se aplica diretamente |
| 4 | Árvore de Decisão, Random Forest | **Modelos principais** do projeto |
| 5 | Validação cruzada (K-Fold), Pipeline Sklearn | Usar `KFold` para avaliação mais robusta |
| 6 | Matriz de confusão, Accuracy, Precision, Recall, F1, `classification_report` | **Métricas obrigatórias** da entrega |
| 7 | Curva ROC, AUC | Complementar à avaliação dos modelos |

### Computer Vision (Aulas 1–6) — prof. Rodrigo Viannini
- **Não obrigatório** para a entrega principal
- Item **EXTRA** para pontuação adicional: CNN para mamografias (dataset CBIS-DDSM)
- Tecnologias: TensorFlow/Keras, ResNet, VGG, Transfer Learning

---

## Decisões técnicas importantes

**Por que recall > accuracy neste contexto?**  
Um falso negativo (paciente com SOP classificada como saudável) tem custo muito maior que um falso positivo. No diagnóstico médico, preferimos errar para o lado da cautela.

**Por que StandardScaler (não MinMaxScaler)?**  
O dataset tem features hormonais com outliers (ex: beta-HCG pode variar muito). StandardScaler é menos sensível a outliers que MinMaxScaler.

**Desequilíbrio de classes (67/33%):**  
Suave o suficiente para funcionar bem. Monitorar recall da classe positiva (SOP=1). Se necessário, usar `class_weight='balanced'` nos modelos.

**Features esperadas com alta importância (baseado na clínica):**  
`Follicle No. (L)`, `Follicle No. (R)`, `AMH(ng/mL)`, `FSH/LH`, `LH(mIU/mL)` — marcadores clínicos conhecidos de SOP.

---

## Arquivos de referência

| Arquivo | Conteúdo |
|---|---|
| [`IADT - Fase 1 - Tech challenge A.pdf`](./IADT%20-%20Fase%201%20-%20Tech%20challenge%20A.pdf) | Enunciado completo do challenge |
| [`pcos_data/PCOS_data_without_infertility.xlsx`](./pcos_data/PCOS_data_without_infertility.xlsx) | Dataset principal (sheet `Full_new`) |
| [`pcos_data/PCOS_infertility.csv`](./pcos_data/PCOS_infertility.csv) | Features adicionais para merge |
| `Machine Learning/` | Aulas 1–4: fundamentos, regressão, PCA, feature scaling |
| `Machine Learning Avancado/` | Aulas 1–7: classificação, KNN/SVM, árvores, validação cruzada, métricas, ROC/AUC |
| `Compute Vision/` | Aulas 1–6: CNN, transfer learning, ResNet/VGG (extra) |
