# Roteiro de Apresentação — Tech Challenge Fase 1
## Diagnóstico de SOP com Machine Learning
**FIAP POSTECH — IA para Devs | Matheus Tomaz**

> **Como usar este roteiro:** Leia cada seção antes de gravar o slide correspondente. As falas em itálico são sugestões de transição. Os **destaques em negrito** são os pontos técnicos que você NÃO pode esquecer. Tempo total estimado: 14–15 minutos.

---

## Slide 1 — Capa (~30 seg)

**O que você verá na tela:** Título, instituição, seu nome.

**Fala:**

> "Olá! Meu nome é Matheus Tomaz. Neste vídeo apresento o Tech Challenge da Fase 1 do curso de IA para Devs da FIAP POSTECH.
>
> O projeto desenvolve um sistema de Machine Learning para apoiar o diagnóstico da Síndrome dos Ovários Policísticos — a SOP — utilizando dados clínicos reais de 541 pacientes coletados em 10 hospitais na Índia.
>
> Vou cobrir todo o pipeline técnico: exploração dos dados, pré-processamento, feature engineering, quatro modelos de ML, avaliação de métricas e explicabilidade com SHAP. Vamos começar."

---

## Slide 2 — O Problema: SOP (~1 min)

**O que você verá na tela:** Contexto clínico + KPIs do dataset.

**Conceitos-chave para dominar:**
- SOP afeta 8–13% das mulheres globalmente (OMS)
- Causa: desequilíbrio hormonal → andrógenos elevados
- Consequências: infertilidade, diabetes tipo 2, risco cardiovascular
- O problema de ML: **classificação binária** (0 = sem SOP, 1 = com SOP)

**Fala:**

> "A Síndrome dos Ovários Policísticos é o distúrbio endócrino mais comum em mulheres em idade reprodutiva. Afeta entre 8 e 13% das mulheres globalmente, segundo a OMS, e muitas chegam ao diagnóstico tarde porque os sintomas são difusos.
>
> Do ponto de vista de Machine Learning, transformamos isso em um problema de classificação binária: dado um conjunto de exames clínicos, o modelo decide se a paciente tem ou não tem SOP.
>
> Os dados são de 541 pacientes, com 44 features clínicas cobrindo desde dados hormonais até comportamento alimentar.
>
> **E aqui está o ponto mais importante do projeto do ponto de vista técnico:** o erro de classificar uma paciente com SOP como saudável — o Falso Negativo — tem custo clínico muito maior do que o erro oposto. Por isso, a métrica que priorizamos é o **Recall**, não a acurácia."

---

## Slide 3 — Dataset (~1 min)

**O que você verá na tela:** Tabela com grupos de features.

**Conceitos-chave para dominar:**
- Dois arquivos: `PCOS_data_without_infertility.xlsx` + `PCOS_infertility.csv`
- Merge pelo `Patient File No.`
- 7 grupos de features: demográficas, hormonais, metabólicas, sintomas, ultrassom, comportamental, reprodutiva
- Target: `PCOS (Y/N)` → 364 (67%) sem SOP, 177 (33%) com SOP

**Fala:**

> "O dataset vem do Kaggle, publicado por Prasoon Kottarathil em 2020. Os dados foram coletados em 10 hospitais do estado de Kerala, na Índia.
>
> Trabalhamos com dois arquivos que precisam de merge: o principal tem dados clínicos gerais, e um CSV complementar adiciona três features de beta-HCG e AMH hormonal. O merge é feito pela coluna Patient File No — o número do prontuário da paciente.
>
> As features cobrem sete grupos, como vocês podem ver na tabela: dados demográficos como IMC e idade; marcadores hormonais como FSH, LH e AMH; dados de ultrassom com número de folículos — que vão ser os mais importantes para o modelo.
>
> Após o merge e limpeza, ficamos com 541 pacientes e 42 features úteis. O target tem um leve desequilíbrio: 67% sem SOP e 33% com SOP."

---

## Slide 4 — EDA: Distribuição e Features (~1 min)

**O que você verá na tela:** Três gráficos — distribuição target, histogramas, boxplots.

**Conceitos-chave para dominar:**
- Distribuição 364/177 — desequilíbrio moderado, não precisa de oversampling
- Histogramas separados por diagnóstico: AMH e FSH/LH têm distribuições muito diferentes
- Boxplots confirmam: folículos e AMH são claramente maiores em pacientes com SOP

**Fala:**

> "O primeiro gráfico confirma o desequilíbrio: 364 sem SOP e 177 com SOP. É moderado — suficiente para preocupar com Recall, mas não exige técnicas como SMOTE.
>
> Os histogramas são reveladores: separando as distribuições por diagnóstico, marcadores hormonais como AMH e a razão FSH/LH têm distribuições completamente diferentes entre os dois grupos. Isso já sugere que serão features importantes.
>
> Os boxplots confirmam: pacientes com SOP têm significativamente mais folículos ovarianos e AMH mais elevado — que são justamente os critérios diagnósticos que os médicos já usam clinicamente.
>
> Essa análise exploratória validou nossas hipóteses clínicas e guiou as decisões de feature engineering que vou mostrar em breve."

---

## Slide 5 — EDA: Sintomas e Correlação (~1 min)

**O que você verá na tela:** Prevalência de sintomas + heatmap de correlação.

**Conceitos-chave para dominar:**
- Sintomas clínicos têm prevalência muito maior em pacientes com SOP
- Heatmap: Follicle No. L e R, AMH e FSH/LH têm correlação mais alta com target
- Features com correlação próxima de 0 serão removidas na feature selection
- Multicolinearidade esperada: L e R têm alta correlação entre si

**Fala:**

> "À esquerda, a prevalência dos sintomas clínicos. A diferença é clara: ganho de peso, crescimento de pelos, escurecimento de pele, queda de cabelo e acne são muito mais frequentes em pacientes com SOP. Isso motivou a criação de uma feature agregadora que vou mostrar a seguir.
>
> À direita, o heatmap de correlação. Os destaques são: os dois contadores de folículos — esquerdo e direito — têm alta correlação com o target, seguidos de AMH e FSH/LH. No outro extremo, algumas features de pressão arterial e frequência cardíaca têm correlação próxima de zero.
>
> O heatmap também mostra multicolinearidade esperada entre folículos esquerdo e direito — que vai motivar a criação de uma feature combinada."

---

## Slide 6 — Pré-processamento (~1 min)

**O que você verá na tela:** Pipeline com 5 etapas + código Python.

**Conceitos-chave para dominar:**
- **Data Leakage**: StandardScaler deve ser `fit` apenas no treino!
- Imputação por mediana → robusto a outliers hormonais
- `stratify=y` na divisão → mantém proporção 67/33 nos dois conjuntos
- `random_state=42` → reprodutibilidade

**Fala:**

> "O pipeline de pré-processamento tem cinco etapas. Vou destacar as mais importantes do ponto de vista técnico.
>
> Na imputação, usamos mediana — não média — porque dados hormonais têm outliers frequentes. A mediana é mais robusta.
>
> A divisão treino/teste usa dois parâmetros críticos: `random_state=42` garante reprodutibilidade, e `stratify=y` garante que a proporção de 67/33 seja mantida nos dois conjuntos. Sem estratificação, poderíamos ter um conjunto de teste desbalanceado por acaso.
>
> **O ponto mais importante:** o StandardScaler é ajustado APENAS no conjunto de treino. Se fitássemos no dataset completo, informação do conjunto de teste contaminaria o treino — isso se chama data leakage e invalida toda a avaliação. Aplicamos o scaler no treino com `fit_transform` e no teste apenas com `transform`."

---

## Slide 7 — Feature Engineering (~1 min)

**O que você verá na tela:** Código das 4 features + justificativas clínicas.

**Conceitos-chave para dominar:**
- `total_foliculos` = Follicle No. L + R → **feature #1 do Random Forest (18.17%)**
- `soma_sintomas` = soma dos 5 sintomas binários → **feature #3 do Random Forest (10.25%)**
- `faixa_imc` = categorização do IMC em 4 faixas (sem lambda — função nomeada)
- `razao_lh_fsh` = LH / FSH → critério diagnóstico clássico (razão > 2 = suspeita de SOP)

**Fala:**

> "Feature engineering é onde o conhecimento de domínio entra em cena. Criamos quatro features novas.
>
> A primeira é o total de folículos: a soma dos contadores esquerdo e direito. Separados, cada um tem importância limitada; combinados, essa feature tornou-se a mais importante do modelo com 18% de relevância.
>
> A segunda é a soma dos sintomas: somamos os 5 sintomas clínicos binários. Individualmente, cada sintoma tem correlação moderada; em conjunto, a carga sintomática total é muito mais informativa.
>
> A terceira categoriza o IMC em 4 faixas — abaixo do peso, normal, sobrepeso e obesidade. Note que usamos uma função nomeada, não lambda — isso é uma exigência do projeto para manter o código didático.
>
> A quarta é a razão LH dividido por FSH. Uma razão acima de 2 é um critério diagnóstico clássico de SOP na medicina. Ao criar essa feature, estamos codificando conhecimento médico diretamente no modelo."

---

## Slide 8 — Feature Selection + Split (~1 min)

**O que você verá na tela:** Código de seleção por correlação + estatísticas do split.

**Conceitos-chave para dominar:**
- Limiar de correlação: `abs(corr) < 0.05` → feature removida
- 45 → 31 features (14 removidas)
- Split: 80% treino (432) / 20% teste (109)
- `stratify=y` mantém a proporção

**Fala:**

> "Após o feature engineering, tínhamos 45 features. Aplicamos uma seleção por correlação com o target: qualquer feature com correlação de Pearson menor que 0.05 em valor absoluto foi removida.
>
> O critério é simples: se uma feature quase não tem relação linear com o target, ela provavelmente só vai adicionar ruído ao modelo. Removemos 14 features — ficamos com 31.
>
> Para a divisão treino/teste, optamos por 80/20 — uma proporção clássica para datasets de tamanho médio. Com 541 amostras, 109 pacientes no conjunto de teste é suficiente para uma avaliação confiável.
>
> O `stratify=y` garante que nos 109 pacientes de teste, a proporção seja mantida: aproximadamente 73 sem SOP e 36 com SOP — espelhando o dataset original."

---

## Slide 9 — Por que Recall? (~1 min)

**O que você verá na tela:** Matriz de confusão conceitual + fórmulas.

**Conceitos-chave para dominar:**
- **Recall = TP / (TP + FN)** — quantos positivos reais foram capturados
- FN: saudável quando tem SOP → consequência clínica grave
- FP: SOP quando é saudável → apenas exame confirmatório adicional
- `class_weight='balanced'` para compensar desequilíbrio de classes

**Fala:**

> "Vamos aprofundar a justificativa para priorizar o Recall.
>
> A matriz de confusão tem quatro células. No canto inferior esquerdo, o Falso Negativo: prevemos que a paciente não tem SOP, mas ela tem. Esse erro significa que ela vai embora sem diagnóstico, sem tratamento, com risco de infertilidade e complicações metabólicas.
>
> O Falso Positivo — prevemos SOP mas ela não tem — é um erro muito mais leve: gera um exame confirmatório adicional que vai corrigir o diagnóstico.
>
> O Recall captura exatamente a taxa de Falsos Negativos: de todas as pacientes com SOP, quantas o modelo identificou corretamente? É essa a pergunta que importa clinicamente.
>
> Para compensar o desequilíbrio de 67/33, todos os modelos foram configurados com `class_weight='balanced'`. Esse parâmetro aumenta o peso das amostras da classe minoritária durante o treinamento, empurrando o modelo a ser mais sensível à classe de SOP."

---

## Slide 10 — Os 4 Modelos (~1 min)

**O que você verá na tela:** Código Python dos 4 modelos + justificativas.

**Conceitos-chave para dominar:**
- Dicionário de modelos → loop de treinamento (código limpo e escalável)
- **Regressão Logística**: baseline interpretável, coeficientes como pesos
- **Árvore de Decisão**: regras explícitas, tende a overfit
- **Random Forest**: ensemble de 100 árvores, reduz overfitting via bagging
- **KNN (k=5)**: baseado em distância, não-paramétrico, sem `class_weight`

**Fala:**

> "Treinamos quatro modelos que cobrem paradigmas diferentes de Machine Learning.
>
> Usamos um dicionário para armazenar os modelos e um loop para treinar e avaliar cada um — isso mantém o código limpo e evita repetição.
>
> A Regressão Logística funciona como baseline: é o modelo mais simples e os coeficientes nos dizem diretamente qual feature empurra para cada diagnóstico.
>
> A Árvore de Decisão gera regras explícitas: se AMH maior que X e folículos maior que Y, então SOP. Boa interpretabilidade, mas tende a overfit em dados ruidosos.
>
> O Random Forest é um ensemble de 100 árvores. Cada árvore treina em um subconjunto aleatório dos dados e das features — bagging. A previsão final é votação da maioria. Isso reduz o overfitting drasticamente.
>
> O KNN com k=5 classifica cada paciente olhando para os 5 vizinhos mais próximos no espaço de features normalizado. É não-paramétrico — não assume distribuição dos dados — e serve de contraste com os modelos paramétricos."

---

## Slide 11 — Resultados (~1 min)

**O que você verá na tela:** Tabela comparativa + K-Fold CV.

**Números que você PRECISA saber de cor:**

| Modelo | Acurácia | Recall | F1 | AUC |
|--------|----------|--------|----|-----|
| **Reg. Logística** | 89.91% | **88.89%** ← melhor | 85.33% | 0.9631 |
| Árvore de Decisão | 86.24% | 80.56% | 79.45% | 0.8701 |
| **Random Forest** | **93.58%** ← melhor | 83.33% | **89.55%** ← melhor | 0.9505 |
| KNN (k=5) | 90.83% | 77.78% | 84.85% | 0.9614 |

**K-Fold (k=5):** RF: 82.89% ±3.25% | KNN: 82.44% ±5.68% | RL: 80.34% ±4.79% | DT: 76.69% ±5.75%

**Fala:**

> "Aqui estão os resultados. Vou destacar os pontos mais relevantes.
>
> Para Recall — nossa métrica prioritária — a Regressão Logística é a vencedora com 88.89%. Isso significa que dos 36 pacientes com SOP no conjunto de teste, ela classificou corretamente 32. Apenas 4 falsos negativos.
>
> Para Acurácia e F1-Score, o Random Forest domina: 93.58% de acurácia e 89.55% de F1. Ele é o modelo mais equilibrado.
>
> O KNN tem o pior Recall — 77.78% — o que seria preocupante em uso clínico.
>
> A validação cruzada com 5 folds confirma os resultados e mostra a variância. O Random Forest tem o menor desvio padrão — 3.25% — o que indica maior estabilidade. O KNN tem maior variância — 5.68% — o que sugere que seu desempenho depende mais de como os dados são divididos.
>
> **Conclusão:** para uso clínico real, priorizamos Recall → Regressão Logística. Para uso geral, o Random Forest é superior em todas as outras métricas."

---

## Slide 12 — Matrizes de Confusão + ROC (~1 min)

**O que você verá na tela:** Matrizes de confusão e curvas ROC.

**Conceitos-chave para dominar:**
- Focar na célula FN de cada matriz (inferior esquerda)
- ROC: curva no espaço TPR × FPR; diagonal = modelo aleatório
- **AUC-ROC > 0.90** em todos os modelos exceto Árvore

**Fala:**

> "Vamos às visualizações. Na esquerda, as matrizes de confusão dos quatro modelos. O que estamos acompanhando é sempre a célula inferior esquerda — os Falsos Negativos.
>
> Regressão Logística: 4 FN. Random Forest: 6 FN. KNN: 8 FN. Árvore de Decisão: 7 FN. Isso confirma quantitativamente o ranking de Recall que vimos na tabela.
>
> À direita, as curvas ROC. A curva plota a taxa de verdadeiros positivos contra a taxa de falsos positivos para todos os possíveis thresholds de decisão. A diagonal seria um modelo aleatório — AUC de 0.5. Quanto mais próxima do canto superior esquerdo, melhor.
>
> A Regressão Logística e o KNN chegam a AUC acima de 0.96. O Random Forest está em 0.95. Todos excelentes. A Árvore isolada fica em 0.87 — o Random Forest, sendo um ensemble de árvores, melhora substancialmente esse número."

---

## Slide 13 — Feature Importance (~1 min)

**O que você verá na tela:** Gráfico de barras + tabela top 6.

**Conceitos-chave para dominar:**
- Feature Importance = contribuição média de cada feature para reduzir impureza nas árvores
- **Top 1: total_foliculos (18.17%)** — criada no feature engineering!
- **Top 3: soma_sintomas (10.25%)** — também criada no feature engineering!
- Features clínicas naturais no top: Follicle R, AMH, FSH/LH

**Fala:**

> "O gráfico de Feature Importance do Random Forest mostra a contribuição relativa de cada variável.
>
> O resultado mais marcante é que as duas features que criamos no Feature Engineering estão no top 3. A total_foliculos — soma dos folículos dos dois ovários — é a feature mais importante do modelo com 18.17%. A soma_sintomas está em terceiro lugar com 10.25%.
>
> Isso é uma validação direta do feature engineering: ao combinar informações relacionadas, criamos sinais mais fortes do que os originais separados.
>
> As features clínicas naturais no ranking — contagem de folículos R e L, AMH e a razão FSH/LH — são exatamente os marcadores que a medicina já sabe que são os mais importantes para o diagnóstico de SOP. O modelo aprendeu isso diretamente dos dados, o que é uma excelente validação da qualidade do dataset e do modelo."

---

## Slide 14 — SHAP Values (~1 min)

**O que você verá na tela:** Summary plot, bar plot, waterfall.

**Conceitos-chave para dominar:**
- SHAP = SHapley Additive exPlanations → teoria dos jogos
- **Summary plot**: cada ponto = uma paciente; cor = valor da feature; posição horizontal = impacto
- **Bar plot**: importância média por feature (semelhante ao Feature Importance mas diferente escala)
- **Waterfall**: explicação individual → como cada feature contribuiu para UMA previsão específica

**Fala:**

> "SHAP é uma técnica baseada na teoria dos jogos que explica quantitativamente a contribuição de cada feature para cada previsão individual.
>
> No Summary Plot à esquerda, cada ponto representa uma paciente. A posição horizontal mostra se a feature empurrou a previsão para SOP — à direita — ou para saudável — à esquerda. A cor indica o valor da feature: vermelho para valores altos, azul para baixos. Vemos claramente que valores altos de total_foliculos — pontos vermelhos à direita — aumentam muito a probabilidade de SOP.
>
> O Bar Plot no centro mostra a importância média absoluta dos valores SHAP — é uma visualização mais limpa da mesma informação.
>
> O Waterfall à direita é a parte mais poderosa: mostra como o modelo chegou a uma previsão específica para uma paciente. Partindo do valor base médio, cada feature adiciona ou subtrai da previsão final. Isso permite explicar para um médico: 'este modelo previu SOP porque esta paciente tem 18 folículos totais e AMH elevado.'
>
> Essa explicabilidade é fundamental para aplicações clínicas reais."

---

## Slide 15 — Conclusão (~1 min)

**O que você verá na tela:** Conquistas e limitações.

**Conceitos-chave para dominar:**
- **Conquista principal**: Recall de 88.89% com apenas 4 FN em 36 casos positivos
- Feature Engineering validado pelas métricas (top 1 e top 3 do RF)
- Limitação principal: dataset geográfico específico (Kerala, Índia)
- Próximos passos: threshold tuning, mais dados, API REST

**Fala:**

> "Para fechar, um balanço honesto do projeto.
>
> Do lado das conquistas: construímos um pipeline completo, reprodutível, com boas práticas de ML. O feature engineering foi validado pelas métricas — nossas features criadas ficaram entre as mais importantes. A Regressão Logística atingiu 88.89% de Recall, com apenas 4 falsos negativos em 36 casos positivos. Isso seria clinicamente aceitável para um sistema de triagem de baixo custo.
>
> Do lado das limitações: o dataset é de Kerala, Índia, e precisa de validação com dados de outras populações antes de qualquer uso real. As 541 amostras são adequadas para ML clássico mas insuficientes para deep learning. E usamos o threshold padrão de 0.5 — em uso real, abaixaríamos esse threshold para aumentar ainda mais o Recall.
>
> Próximos passos naturais seriam experimentar XGBoost e outros gradiente boosting, fazer threshold tuning explícito, coletar mais dados e desenvolver uma API REST para integrar o modelo a sistemas hospitalares.
>
> Obrigado pela atenção! O notebook completo está disponível no repositório, com todas as células executadas e os gráficos gerados automaticamente."

---

## Dicas para a Gravação

**Antes de gravar:**
- [ ] Abra o PowerPoint e revise todas as notas do apresentador (estão visíveis na visão do apresentador)
- [ ] Tenha o notebook Jupyter aberto em outra tela para mostrar o código ao vivo se quiser
- [ ] Pratique os slides 11 e 12 — têm os números mais densos

**Durante a gravação:**
- Não precisa ler o roteiro literalmente — use como guia de pontos-chave
- Mostre o código nas notas quando falar de pré-processamento e feature engineering
- Ao comentar os gráficos, aponte para elementos específicos com o cursor

**Ordem de prioridade se o tempo apertar:**
1. Slide 9 (Por que Recall) — o mais conceitual e diferenciador
2. Slide 7 (Feature Engineering) — mostra iniciativa técnica
3. Slide 11 (Resultados) — os números que o avaliador vai conferir
4. Slide 14 (SHAP) — diferencial técnico

**Vocabulário técnico para usar:**
- "pipeline de ML" (não "processo")
- "desequilíbrio de classes" (não "mais de um grupo que o outro")
- "data leakage" — mencionar e explicar brevemente
- "ensemble" ao falar do Random Forest
- "SHAP values" (pronunciar "SHAP")
- "AUC-ROC" (pronunciar letra por letra)
- "K-Fold cross-validation" ao falar da validação cruzada

---

## Referências Rápidas

**Arquivo do notebook:** `code/pcos_diagnostico_executado.ipynb`  
**Gráficos:** `code/graficos/` (12 imagens)  
**PDF do relatório:** `Tech_Challenge_Fase1_PCOS_Relatorio.pdf`  
**Dataset:** [Kaggle PCOS](https://www.kaggle.com/datasets/prasoonkottarathil/polycystic-ovary-syndrome-pcos)

---

*Roteiro gerado para o Tech Challenge Fase 1 — FIAP POSTECH IA para Devs — Maio 2026*
