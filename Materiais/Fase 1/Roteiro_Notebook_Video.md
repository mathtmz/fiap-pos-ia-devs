# Roteiro: Apresentação do Jupyter Notebook
## Tech Challenge Fase 1 — FIAP POSTECH IA para Devs
### Arquivo: `pcos_diagnostico_executado.ipynb`

> **Como usar:** Abra o notebook executado no Jupyter. Navegue célula a célula conforme o roteiro. As falas são sugestões — adapte ao seu ritmo. Tempo total: ~15 minutos.
>
> **Dica de gravação:** Use o modo "presentation view" do Jupyter ou aumente a fonte do browser (Ctrl+ / Cmd+) para o código ficar legível no vídeo.

---

## ⏱ Mapa de tempo

| Seção | Células | Tempo sugerido |
|-------|---------|----------------|
| Introdução + imports | 00–02 | 1 min |
| Carregamento dos dados | 03–07 | 1.5 min |
| EDA | 08–15 | 2 min |
| Pré-processamento | 16–18 | 1 min |
| Feature Engineering | 19–27 | 2.5 min |
| Modelagem | 28–43 | 2 min |
| Avaliação | 44–51 | 2 min |
| Explicabilidade | 52–59 | 2 min |
| Conclusão | 60–62 | 1 min |
| **Total** | | **~15 min** |

---

## 🎬 ABERTURA (antes de abrir o notebook)

> "Olá! Meu nome é Matheus Tomaz, e neste vídeo apresento o Tech Challenge da Fase 1 do curso de IA para Devs da FIAP POSTECH.
>
> O projeto é sobre diagnóstico de Síndrome dos Ovários Policísticos usando Machine Learning. Vou apresentar diretamente pelo Jupyter Notebook, mostrando o código, os outputs e os gráficos exatamente como foram desenvolvidos.
>
> Vamos começar."

**[Abra o Jupyter no arquivo `pcos_diagnostico_executado.ipynb`]**

---

## 📌 CÉLULA 00 — Título e contexto do problema

**O que está na tela:** markdown com título, contexto clínico, descrição do dataset e estrutura do notebook.

> "A primeira célula do notebook apresenta o problema. A SOP — Síndrome dos Ovários Policísticos — é o distúrbio endócrino mais comum em mulheres em idade reprodutiva, afetando entre 8 e 13% da população feminina segundo a OMS.
>
> O objetivo do projeto é construir um modelo capaz de, a partir de dados clínicos e laboratoriais, classificar se uma paciente tem ou não tem SOP. O modelo serve como apoio ao diagnóstico — o médico sempre tem a última palavra.
>
> O dataset tem 541 pacientes, 44 variáveis clínicas, e foi coletado em 10 hospitais de Kerala, na Índia."

---

## 📌 CÉLULA 01–02 — Importação das bibliotecas

**O que está na tela:** célula markdown + célula de código com os imports.

> "A segunda seção são os imports. Reparem na organização: agrupei as bibliotecas por responsabilidade — manipulação de dados, visualização, pré-processamento, modelos e métricas.
>
> Um detalhe importante: a linha `SEMENTE_ALEATORIA = 42` define uma constante global usada em todos os lugares que aceitam `random_state`. Isso garante reprodutibilidade total — qualquer pessoa rodando esse notebook vai obter exatamente os mesmos resultados.
>
> O output `Bibliotecas carregadas com sucesso!` confirma que o ambiente está configurado."

**Destaque técnico para mencionar:**
- `SEMENTE_ALEATORIA = 42` → reprodutibilidade
- `shap` → biblioteca de explicabilidade (explica cada previsão individual)

---

## 📌 CÉLULAS 03–07 — Carregamento dos dados

**O que está na tela:** markdown explicando a investigação do merge + células de código com outputs.

> "Aqui temos uma parte que gosto de destacar porque mostra rigor de análise. O dataset vem de dois arquivos: um Excel com os dados principais e um CSV complementar. A ideia inicial era fazer um merge pelos IDs dos pacientes.
>
> Mas antes de fazer o merge cegamente, investigamos se o merge era realmente necessário. Executamos três verificações:
> primeiro, os IDs são os mesmos pacientes — o CSV usa o prefixo 10000 diferente do Excel;
> segundo, comparamos o campo PCOS: 100% idêntico nas 541 linhas, zero divergências;
> terceiro, comparamos o AMH: diferença máxima de 0.0000."

**Aponte para o output da célula 04:**
```
Colunas exclusivas do CSV (não existem no Excel): nenhuma
Diferença máxima AMH entre Excel e CSV: 0.0000 (0 = dados idênticos)
```

> "Resultado: todas as colunas do CSV já existem no Excel com valores idênticos. O merge seria redundante. Utilizamos apenas o Excel — uma decisão documentada no próprio notebook.
>
> Após remover 3 colunas que não têm valor preditivo — o índice sequencial, o ID da paciente e uma coluna vazia gerada pelo Excel — ficamos com 542 pacientes e 42 colunas úteis."

**Aponte para o output da célula 06:**
```
Dataset final: 541 pacientes, 42 colunas
```

> "A célula 07 faz uma limpeza de tipos: duas colunas — AMH e beta-HCG — tinham o caractere 'a' como erro de digitação. O `pd.to_numeric` com `errors='coerce'` converte esses valores inválidos para NaN, que tratamos na etapa de imputação."

---

## 📌 CÉLULAS 08–15 — Exploração dos dados (EDA)

**O que está na tela:** outputs de `dados.info()`, `describe()`, gráficos.

> "A análise exploratória tem três partes: visão geral dos dados, distribuição das features clínicas e prevalência de sintomas.
>
> O `dados.info()` mostra que quase todas as colunas estão completas — apenas 4 NaN no total, distribuídos em 3 colunas. Isso é um dataset muito limpo para dados médicos reais.
>
> O `dados.describe()` mostra estatísticas básicas. Notem que a média do target PCOS é 0.33, confirmando que 33% das pacientes têm SOP."

**Aponte para o output da célula 11:**
```
Sem SOP (0): 364 pacientes (67.3%)
Com SOP (1): 177 pacientes (32.7%)
```

> "O gráfico de distribuição do target confirma o desequilíbrio de 67/33. Esse nível de desequilíbrio é moderado — não é tão severo a ponto de precisarmos de oversampling artificial, mas é suficiente para nos preocuparmos com o Recall, e não só com a acurácia."

**Aponte para o gráfico de histogramas — células 13–14:**

> "Esses histogramas e boxplots são onde a EDA realmente brilha. Para cada feature importante, plotamos a distribuição separada por diagnóstico — verde para sem SOP, vermelho para com SOP.
>
> As separações mais claras estão em AMH — o hormônio anti-Mülleriano — e em Follicle No. L e R — a contagem de folículos nos ovários esquerdo e direito. Essas são exatamente as features que a medicina clínica já usa para diagnosticar SOP. O modelo vai confirmar isso nos resultados de feature importance."

**Aponte para o output de prevalência de sintomas — célula 15:**
```
                      Com SOP (%)  Sem SOP (%)
Weight gain(Y/N)             68.4         22.8
hair growth(Y/N)             57.1         12.9
Skin darkening (Y/N)         62.1         15.4
```

> "O gráfico de sintomas mostra diferenças marcantes: ganho de peso ocorre em 68% das pacientes com SOP contra 23% das saudáveis. Crescimento de pelos: 57% versus 13%. Essa observação motivou a criação de uma feature de engenharia que veremos a seguir."

---

## 📌 CÉLULAS 16–18 — Pré-processamento

**O que está na tela:** código de imputação e encoding.

> "O pré-processamento tem duas etapas principais: imputação de valores ausentes e encoding de variáveis categóricas.
>
> Para a imputação, criei uma função reutilizável chamada `preencher_ausentes_com_mediana`. Por que mediana e não média? Dados hormonais — como AMH e beta-HCG — têm outliers frequentes. A mediana é mais robusta: um único valor extremo não distorce o preenchimento."

**Aponte para o output da célula 17:**
```
"Marraige Status (Yrs)": 1 NaN → mediana = 7.00
"II    beta-HCG(mIU/mL)": 1 NaN → mediana = 1.99
"AMH(ng/mL)": 1 NaN → mediana = 3.70
"Fast food (Y/N)": 1 NaN → mediana = 1.00
Total preenchido: 4 | Ausentes restantes: 0
```

> "Preenchemos 4 valores ausentes. Após isso, o dataset está completo — zero NaN.
>
> Para o Blood Group, usamos LabelEncoder para converter os tipos sanguíneos em inteiros. O output da célula 18 mostra que não havia colunas de texto a converter — o Blood Group já estava numérico após a leitura. A segunda passada de imputação confirma que continuamos com zero ausentes."

---

## 📌 CÉLULAS 19–27 — Feature Engineering ⭐ (parte mais rica)

**O que está na tela:** markdown explicando a motivação + células de código.

> "A seção 5 é, na minha opinião, a mais interessante do projeto do ponto de vista técnico. Feature Engineering é criar novas variáveis a partir das existentes, combinando conhecimento de domínio com os padrões que observamos na EDA."

**Célula 21 — as 4 features criadas:**

> "Criamos 4 features novas.
>
> A primeira é `total_foliculos` — simplesmente a soma dos folículos dos ovários esquerdo e direito. A motivação clínica é o critério de Rotterdam: um dos critérios diagnósticos oficiais de SOP é ter 12 ou mais folículos em pelo menos um ovário. Somar os dois lados dá ao modelo uma visão agregada diretamente ligada a esse critério.
>
> A segunda é `soma_sintomas` — somamos os 5 sintomas binários: ganho de peso, crescimento de pelos, escurecimento de pele, queda de cabelo e acne. A ideia é que pacientes com SOP tendem a acumular múltiplos sintomas ao mesmo tempo — isso cria um índice de carga sintomática.
>
> A terceira é `faixa_imc` — transformamos o IMC contínuo em categorias clínicas da OMS: abaixo do peso, normal, sobrepeso, obesidade e obesidade severa. Isso captura limiares biológicos reais que um valor numérico bruto pode não transmitir bem. Note que usei uma função `pd.cut` com limites explícitos — sem lambda, como exige o projeto.
>
> A quarta é `razao_lh_fsh` — a razão LH dividido por FSH. Uma razão maior que 2 é um marcador clínico estabelecido de SOP. O dataset já tinha FSH/LH — criamos a inversa para que valores altos correspondam a maior indicativo de SOP."

**Aponte para o output da célula 22:**
```
Correlação com PCOS (Y/N):
  total_foliculos     : +0.6603
  soma_sintomas       : +0.5802
  faixa_imc           : +0.1648
  razao_lh_fsh        : +0.0648

Comparação com features originais:
  Follicle No. (L)    : +0.6033
  Follicle No. (R)    : +0.6483
  total_foliculos     : +0.6603   ← melhor que ambos separados
  soma_sintomas       : +0.5802   ← feature nova, alta correlação
```

> "Esse output é a validação quantitativa do feature engineering. `total_foliculos` tem correlação de 0.66 com o target — melhor do que Follicle L (0.60) e Follicle R (0.64) separados. Ao combinar os dois ovários, criamos um sinal mais forte. `soma_sintomas` tem 0.58 de correlação — uma feature completamente nova com alto poder preditivo."

**Célula 25–26 — Feature Selection:**

> "Com as novas features, temos 45 features no total. A seleção elimina as que têm pouco poder discriminativo: qualquer feature com correlação absoluta menor que 0.05 com o target é removida."

**Aponte para o output da célula 26:**
```
Features com |correlação| < 0.05 (candidatas à remoção):
  RBS(mg/dl)             : 0.0489
  PRG(ng/mL)             : 0.0438
  BP _Diastolic (mmHg)   : 0.0380
  ...
  FSH/LH                 : 0.0183
  FSH(mIU/mL)            : 0.0303
Total: 14 features serão descartadas
```

> "Catorze features removidas — de 45 para 31. Reparem num detalhe interessante: `FSH/LH` e `FSH(mIU/mL)` foram removidas por baixa correlação com o target. Mas ao mesmo tempo, `razao_lh_fsh` — a nossa feature criada que é essencialmente o inverso de FSH/LH — tem correlação maior, 0.065. Isso mostra que a direção da razão importa: valores altos de LH/FSH são mais indicativos de SOP do que os valores de FSH/LH."

**Célula 29 — resultado da seleção:**

> "O resultado: 45 features originais, 31 após o filtro, 14 removidas."

**Célula 31 — split treino/teste:**

> "A divisão 80/20. O parâmetro `stratify=y` é crítico: garante que a proporção de 33% de SOP seja mantida tanto no treino quanto no teste."

**Aponte para o output:**
```
Treino: 432 pacientes | Teste: 109 pacientes
Proporção SOP treino: 32.6% | teste: 33.0%
```

> "Perfeito — 32.6% no treino e 33.0% no teste. Praticamente idênticos."

**Célula 33 — StandardScaler:**

> "Normalizamos com StandardScaler. A regra de ouro: `fit` apenas no treino — depois `transform` em ambos. O output confirma que o treino normalizado tem média zero e desvio padrão 1, exatamente o esperado do z-score."

**Aponte para o output:**
```
Média no treino normalizado (esperado ~0): 0.000000
Desvio padrão no treino normalizado (~1):  1.000000
```

---

## 📌 CÉLULAS 34–43 — Modelagem

**O que está na tela:** markdown com tabela dos 4 modelos + células de treinamento.

> "A seção 6 treina os quatro modelos. Antes de entrar no código, veja a tabela no markdown: cada modelo tem uma justificativa pedagógica ligada às aulas do curso e uma justificativa técnica."

**Célula 36 — Regressão Logística:**

> "O primeiro modelo é a Regressão Logística. Três parâmetros importantes: `max_iter=1000` porque o dataset tem 31 features e o otimizador precisa de mais iterações para convergir; `random_state=42` para reprodutibilidade; e `class_weight='balanced'` — esse parâmetro faz o algoritmo dar mais peso às amostras da classe minoritária durante o treinamento, compensando o desequilíbrio 67/33."

**Célula 38 — Árvore de Decisão:**

> "A Árvore usa `max_depth=5` como regularização: limitar a profundidade evita que a árvore memorize o treino — overfitting. Usamos `criterion='entropy'` que mede o ganho de informação — a redução da entropia — em cada divisão."

**Célula 40 — Random Forest:**

> "O Random Forest é um ensemble de 100 árvores independentes. Cada árvore é treinada em um subconjunto aleatório das amostras e das features — é o bagging. A previsão final é votação da maioria. `max_depth=10` é um pouco maior que a Árvore individual porque o ensemble em si já regulariza — 100 árvores com overfitting individual tendem a cancelar os erros entre si."

**Célula 42 — KNN com busca de k:**

> "O KNN tem um passo extra: buscamos o melhor k com validação cruzada antes de treinar o modelo final."

**Aponte para o output:**
```
Testando diferentes valores de k:
  k= 3: F1 médio = 79.24%
  k= 5: F1 médio = 82.44%
  k= 7: F1 médio = 77.84%
  ...
Melhor k escolhido: 5 (F1 = 82.44%)
```

> "K=5 venceu com F1 de 82.44%. A busca de hiperparâmetro foi feita no conjunto de treino com K-Fold — o conjunto de teste nunca foi tocado nessa decisão, o que é correto metodologicamente.
>
> Uma observação: KNN não aceita `class_weight`. Compensamos isso com a normalização — sem o StandardScaler, features com escala maior dominariam o cálculo de distância euclidiana."

---

## 📌 CÉLULAS 44–51 — Avaliação dos modelos

**O que está na tela:** classification reports, matrizes de confusão, curvas ROC, K-Fold.

**Célula 45 — Classification Reports:**

> "A função `exibir_metricas` organiza os resultados de forma consistente para todos os modelos. Vamos ver o output."

**Aponte para os resultados:**
```
Regressão Logística:
  Acurácia: 89.91%  |  Recall: 88.89% ← MELHOR  |  F1: 85.33%

Árvore de Decisão:
  Acurácia: 86.24%  |  Recall: 80.56%  |  F1: 79.45%

Random Forest:
  Acurácia: 93.58% ← MELHOR  |  Recall: 83.33%  |  F1: 89.55% ← MELHOR

KNN (k=5):
  Acurácia: 90.83%  |  Recall: 77.78%  |  F1: 84.85%
```

> "Para Recall — nossa métrica prioritária — a Regressão Logística é a vencedora com 88.89%. Isso significa que dos 36 pacientes com SOP no conjunto de teste, o modelo identificou corretamente 32. Apenas 4 falsos negativos.
>
> O Random Forest tem o melhor equilíbrio geral: maior acurácia e melhor F1. O KNN tem o pior Recall — 77.78% — o que em uso clínico real seria preocupante.
>
> Vale notar que no classification report do Regressão Logística, a precision da classe Com SOP é 82% mas o recall é 89% — isso é exatamente o `class_weight='balanced'` em ação: priorizamos identificar todos os casos positivos, aceitando alguns falsos positivos a mais."

**Célula 47 — Matrizes de confusão:**

> "As matrizes de confusão visualizam isso graficamente. O número crítico é a célula inferior esquerda — Falsos Negativos.
>
> Regressão Logística: 4 FN. Random Forest: 6 FN. Árvore: 7 FN. KNN: 8 FN.
>
> Olhando assim, a hierarquia clínica está clara."

**Célula 49 — Curvas ROC:**

> "As curvas ROC plotam a taxa de verdadeiros positivos contra a taxa de falsos positivos para todos os possíveis thresholds de decisão. A diagonal cinza representa um modelo aleatório — AUC de 0.5. Quanto mais próxima do canto superior esquerdo, melhor.
>
> Regressão Logística: AUC 0.9631. KNN: 0.9614. Random Forest: 0.9505. Árvore isolada: 0.8701. Todos excelentes — e o Random Forest ensemble melhora substancialmente o 0.87 da Árvore isolada."

**Célula 51 — K-Fold:**

> "A validação cruzada com 5 folds dá uma estimativa mais robusta do desempenho — usamos 5 partições diferentes do conjunto de treino."

**Aponte para o output:**
```
Modelo                   Média F1    Desvio Padrão
Regressão Logística       80.34%  ±4.79%
Árvore de Decisão         76.69%  ±5.75%
Random Forest             82.89%  ±3.25%
KNN (k=5)                 82.44%  ±5.68%
```

> "O Random Forest tem o melhor F1 médio — 82.89% — E o menor desvio padrão — 3.25%. Isso significa que é o modelo mais estável: seu desempenho varia pouco dependendo de como os dados são divididos.
>
> O KNN tem F1 similar mas variância maior — 5.68% — indicando que é mais sensível à amostragem. Isso faz sentido: KNN depende diretamente dos vizinhos disponíveis em cada fold."

---

## 📌 CÉLULAS 52–59 — Explicabilidade

**O que está na tela:** Feature Importance e SHAP values.

**Células 53–54 — Feature Importance:**

> "A seção 8 é sobre explicabilidade — fundamental para aplicações clínicas.
>
> A Feature Importance do Random Forest mede a contribuição média de cada feature para reduzir a impureza nas árvores. Veja o output."

**Aponte para o output da célula 53:**
```
             feature  importancia
     total_foliculos     0.181682   ← #1 (criada no FE!)
    Follicle No. (R)     0.149148   ← #2
       soma_sintomas     0.102549   ← #3 (criada no FE!)
    Follicle No. (L)     0.086108   ← #4
    hair growth(Y/N)     0.036746
          AMH(ng/mL)     0.034826
```

> "O resultado principal: as duas features que criamos no Feature Engineering estão no top 3. `total_foliculos` é a feature número 1 com 18.2% de importância. `soma_sintomas` está em terceiro com 10.3%.
>
> Isso é a validação definitiva do feature engineering: ao combinar informações relacionadas, criamos sinais mais fortes do que os originais separados. E confirma que o modelo aprendeu os mesmos padrões que a medicina clínica já conhece — folículos e hormônios como principais marcadores de SOP."

**Células 55–58 — SHAP:**

> "SHAP vai além da importância global — explica cada previsão individual usando a teoria dos jogos de Shapley.
>
> O Summary Plot mostra: cada ponto é uma paciente. A posição horizontal indica a direção do impacto — à direita aumenta probabilidade de SOP, à esquerda diminui. A cor indica o valor da feature: vermelho para alto, azul para baixo.
>
> Veja `total_foliculos` no topo: pontos vermelhos concentrados à direita — valores altos de folículos empurram fortemente o diagnóstico para SOP. Pontos azuis à esquerda — poucos folículos afasta o diagnóstico. Exatamente o que esperaríamos clinicamente.
>
> O Bar Plot mostra a importância média absoluta dos SHAP values — uma visão mais limpa da mesma informação."

**Célula 59 — SHAP Waterfall individual:**

> "Aqui está a parte mais poderosa do ponto de vista clínico: a explicação de uma previsão individual."

**Aponte para o output:**
```
Paciente #0:
  Real:              Com SOP
  Previsto:          Sem SOP
  Prob. de SOP:      3.0%
```

> "Interessante — esse caso específico é um erro do modelo: a paciente de fato tem SOP, mas o Random Forest previu 'Sem SOP' com 97% de confiança. É um falso negativo.
>
> O Waterfall mostra exatamente por que o modelo errou nesse caso: as features dessa paciente em particular tinham valores que não correspondiam ao padrão típico de SOP — por isso ele calculou apenas 3% de probabilidade.
>
> Isso ilustra perfeitamente a limitação dos modelos estatísticos: eles acertam na maioria dos casos, mas existem pacientes atípicos que fogem do padrão aprendido. Essa é exatamente a razão pela qual o modelo deve ser um apoio ao diagnóstico médico, não um substituto."

---

## 📌 CÉLULAS 60–62 — Resumo e Conclusão

**Célula 61 — tabela final:**

> "A célula 61 compila os resultados finais de forma organizada."

**Aponte para o output:**
```
=== RESUMO COMPARATIVO DOS 4 MODELOS ===
                     Acurácia (%)  Recall (%)  F1-Score (%)  AUC-ROC
Regressão Logística         89.91       88.89         85.33   0.9631
Árvore de Decisão           86.24       80.56         79.45   0.8701
Random Forest               93.58       83.33         89.55   0.9505
KNN (k=5)                   90.83       77.78         84.85   0.9614
```

> "Com esses números em mãos, a resposta às perguntas do avaliador é direta: qual é o melhor modelo?
>
> Depende do critério. Para uso clínico de triagem, onde minimizar falsos negativos é prioritário, a Regressão Logística ganha com 88.89% de Recall. Para uso geral, onde equilíbrio de métricas importa, o Random Forest é superior em Acurácia e F1."

**Célula 62 — Conclusão:**

> "A conclusão discute quatro pontos.
>
> Primeiro, o que o Feature Engineering acrescentou: `total_foliculos` e `soma_sintomas` ficaram entre as features mais importantes — validação quantitativa da etapa.
>
> Segundo, o que aprendemos com os 4 modelos: cada paradigma tem seus pontos fortes. A Regressão é mais conservadora e segura para triagem. O Random Forest é mais equilibrado. O KNN é intuitivo mas tem maior variância. A Árvore isolada é a mais explicável individualmente.
>
> Terceiro, os modelos podem ser usados na prática? Sim, como ferramentas de triagem, acelerando o processo em unidades com alto volume de pacientes. Mas sempre como apoio — nunca substituindo o julgamento clínico.
>
> Quarto, as limitações honestas: 541 pacientes é um dataset pequeno para generalização ampla, os dados são de Kerala e podem não refletir outras populações, e o modelo não foi testado prospectivamente em cenário clínico real."

---

## 🎬 ENCERRAMENTO

> "Isso conclui a apresentação do Tech Challenge Fase 1. Passamos por todo o pipeline de Machine Learning: carregamento e limpeza dos dados, análise exploratória, pré-processamento com atenção a data leakage, feature engineering baseado em conhecimento clínico, treinamento e comparação de 4 modelos, avaliação com múltiplas métricas e validação cruzada, e explicabilidade com SHAP.
>
> O notebook está disponível no repositório com todas as células executadas e os gráficos gerados automaticamente. Obrigado!"

---

## 📚 Guia de Estudo — Conceitos que o Avaliador Pode Perguntar

### Data Leakage
**Pergunta:** "Por que você fez `fit` do StandardScaler só no treino?"
**Resposta:** Se fitássemos no dataset completo, as estatísticas de média e desvio padrão do conjunto de teste contaminariam o treino. Em produção, o scaler nunca terá acesso a dados futuros — precisamos simular isso na avaliação.

### Stratify
**Pergunta:** "O que faz o `stratify=y`?"
**Resposta:** Garante que a proporção de classes positivas e negativas seja mantida nos dois conjuntos após o split. No output vemos: 32.6% no treino e 33.0% no teste — praticamente idênticos. Sem stratify, poderíamos ter um conjunto de teste desbalanceado por acaso.

### Class Weight
**Pergunta:** "Por que `class_weight='balanced'`?"
**Resposta:** Com desequilíbrio 67/33, um modelo treinado sem compensação tende a favorecer a classe majoritária. O `balanced` aumenta o peso dos erros na classe minoritária (SOP) durante o treinamento, empurrando o modelo a ser mais sensível aos casos positivos — aumentando o Recall.

### Recall vs. Acurácia
**Pergunta:** "Por que Recall é mais importante que Acurácia?"
**Resposta:** Um Falso Negativo — paciente com SOP classificada como saudável — tem custo clínico muito maior: ela vai embora sem diagnóstico e sem tratamento, com risco de infertilidade e complicações metabólicas. Um Falso Positivo gera apenas um exame confirmatório adicional. O Recall captura diretamente a taxa de FN: TP / (TP + FN).

### Por que a Regressão Logística tem maior Recall que o RF?
**Pergunta:** "O Random Forest não deveria ser sempre melhor?"
**Resposta:** Não necessariamente para todas as métricas. O RF tem maior AUC e F1, mas a Regressão Logística com `class_weight='balanced'` calibra melhor o threshold para a classe positiva nesse dataset específico. O trade-off entre Recall e Precision fica em pontos diferentes para cada modelo.

### K-Fold CV
**Pergunta:** "Para que serve a validação cruzada se você já tem um conjunto de teste?"
**Resposta:** O conjunto de teste dá a avaliação final no pior caso — dados nunca vistos. O K-Fold no conjunto de treino serve para comparar modelos com mais robustez, estimar a variância do desempenho (o desvio padrão) e guiar escolhas como o k do KNN, sem tocar o conjunto de teste.

### SHAP
**Pergunta:** "O que são SHAP values?"
**Resposta:** SHAP vem de SHapley Additive exPlanations. Para cada previsão individual, o SHAP calcula quanto cada feature contribuiu para o desvio da previsão em relação à previsão média do modelo (expected value). Baseado na teoria dos jogos de Shapley — a contribuição de cada "jogador" (feature) é calculada considerando todas as possíveis combinações de features.

### Feature Engineering
**Pergunta:** "Como você sabe que o feature engineering foi útil?"
**Resposta:** Duas evidências quantitativas: (1) `total_foliculos` tem correlação 0.66 com o target — melhor que Follicle L (0.60) ou R (0.64) separados. (2) As duas features criadas — `total_foliculos` e `soma_sintomas` — ficaram em 1º e 3º na Feature Importance do Random Forest, com 18.2% e 10.3% respectivamente.

### Investigação do CSV
**Pergunta:** "Por que não fez o merge com o CSV?"
**Resposta:** Antes de fazer o merge, investigamos se ele era necessário. Verificamos que todas as colunas do CSV já existem no Excel com valores idênticos — a diferença máxima de AMH entre os arquivos foi de 0.0000. O merge seria redundante e adicionaria complexidade desnecessária. O notebook documenta essa investigação explicitamente.

---

## 🔢 Números para Decorar

| Dado | Valor |
|------|-------|
| Total de pacientes | 541 |
| Features após limpeza | 42 |
| Features criadas (FE) | 4 |
| Features após seleção | 31 |
| Features removidas | 14 |
| Amostras treino | 432 (80%) |
| Amostras teste | 109 (20%) |
| Recall — Reg. Logística | **88.89%** (melhor) |
| Recall — Random Forest | 83.33% |
| Recall — Árvore | 80.56% |
| Recall — KNN k=5 | 77.78% |
| Acurácia — Random Forest | **93.58%** (melhor) |
| F1 — Random Forest | **89.55%** (melhor) |
| AUC — Reg. Logística | **0.9631** (melhor) |
| K-Fold RF F1 | 82.89% ± 3.25% |
| Feature Importance #1 | total_foliculos: 18.17% |
| Feature Importance #3 | soma_sintomas: 10.25% |
| FN — Reg. Logística | **4** (menor) |
| FN — KNN | 8 (maior) |
| k do KNN | 5 (escolhido por CV) |

---

*Roteiro gerado a partir do arquivo `pcos_diagnostico_executado.ipynb` — FIAP POSTECH IA para Devs — Maio 2026*
