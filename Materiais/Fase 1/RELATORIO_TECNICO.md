# Relatório Técnico — Tech Challenge Fase 1

**FIAP POSTECH — IA para Devs**  
**Aluno:** Matheus Araujo Tomaz  
**Tema:** Sistema de apoio ao diagnóstico de Síndrome dos Ovários Policísticos (SOP) com Machine Learning

---

## 1. Introdução e escolha do problema

A Síndrome dos Ovários Policísticos é uma das condições hormonais mais comuns entre mulheres em idade reprodutiva, com estimativas que variam entre 8% e 13% dessa população. Apesar de ser prevalente, o diagnóstico ainda chega tarde para muitas pacientes — seja por falta de acesso, seja pela variedade de sintomas que se confundem com outras condições.

A motivação para esse projeto partiu justamente desse gap: se temos dados clínicos disponíveis, como exames hormonais, ultrassonografia e sintomas reportados pelas pacientes, é possível treinar um modelo que ajude o profissional de saúde a identificar casos com maior suspeita de SOP mais rapidamente?

O objetivo não é substituir o médico — isso seria irresponsável e clinicamente inviável — mas sim criar uma ferramenta que funcione como triagem, priorizando casos que merecem atenção mais urgente dentro de uma fila de atendimento.

---

## 2. Dataset

O dataset utilizado foi o **Polycystic Ovary Syndrome (PCOS)**, disponível no Kaggle, coletado por Prasoon Kottarathil a partir de 10 hospitais do estado de Kerala, Índia, em 2020. O arquivo principal contém 541 pacientes com 44 variáveis clínicas — desde dados básicos como peso, altura e IMC, até exames hormonais (FSH, LH, AMH, TSH), dados de ultrassonografia (contagem e tamanho de folículos, espessura do endométrio) e sintomas clínicos autoreportados (ganho de peso, crescimento de pelos, acne, entre outros).

O dataset vem dividido em dois arquivos: o Excel com os dados clínicos completos e um CSV com exames complementares. Antes de qualquer análise, foi feita uma investigação para entender se o merge era necessário. Ao comparar os dois arquivos, percebemos que os IDs não coincidem diretamente — o Excel usa sequência 1 a 541 e o CSV usa 10001 a 10541. Para garantir que se tratavam dos mesmos pacientes, comparamos o diagnóstico de SOP linha a linha e o valor de AMH, que é uma das variáveis compartilhadas: zero divergências em ambas as verificações. A conclusão foi que o CSV não traz nenhuma coluna nova em relação ao Excel — todas as variáveis já estão presentes no arquivo principal. Por isso, trabalhamos apenas com o Excel, que é a fonte completa.

A variável alvo é `PCOS (Y/N)`, binária: 0 para pacientes sem SOP e 1 para pacientes com SOP. A distribuição ficou em 364 casos negativos (67,3%) e 177 positivos (32,7%) — um desequilíbrio moderado que precisou ser considerado na modelagem.

---

## 3. Análise exploratória de dados

A primeira etapa foi entender o que os dados têm a dizer antes de qualquer transformação. Aqui algumas observações que guiaram as decisões seguintes:

**Contagem de folículos ovarianos** foi a variável que mais chamou atenção. Pacientes com SOP apresentam distribuições visivelmente mais altas tanto para o ovário esquerdo quanto para o direito. Isso já era esperado — um dos critérios do diagnóstico de Rotterdam para SOP é exatamente a presença de 12 ou mais folículos por ovário no ultrassom.

**AMH (Hormônio Antimülleriano)** também mostrou diferença clara entre os grupos. Valores elevados de AMH indicam maior reserva ovariana, uma característica associada à SOP.

**Sintomas clínicos** apresentaram diferenças bem marcadas. Ganho de peso foi reportado por 68,4% das pacientes com SOP contra 22,8% das sem SOP. Crescimento de pelos (57,1% vs 12,9%) e escurecimento da pele (62,1% vs 15,4%) seguiram o mesmo padrão. Isso faz sentido clínico: esses sintomas são consequência do excesso de andrógenos que caracteriza a síndrome.

**Ciclo menstrual irregular** (`Cycle R/I`) teve correlação de 0,40 com o diagnóstico — a irregularidade menstrual é um dos sinais mais clássicos da SOP.

Um ponto que ficou claro na EDA: não existem variáveis isoladas suficientes para o diagnóstico. A SOP é uma síndrome, ou seja, um conjunto de manifestações. Isso motivou a criação de features que combinam diferentes dimensões do quadro clínico, descrita na seção seguinte.

---

## 4. Pré-processamento

O dataset chegou bastante limpo — apenas 4 valores ausentes em 541 registros, todos em variáveis diferentes. Dois deles vieram de um erro de digitação: a coluna AMH continha o valor `"a"` em um registro, claramente um equívoco de entrada de dados. Esses casos foram tratados com `pd.to_numeric(..., errors='coerce')` para converter para NaN e depois preenchidos com a mediana da coluna.

A escolha da mediana ao invés da média foi intencional: dados médicos frequentemente têm outliers legítimos (um exame hormonal fora do padrão não é necessariamente erro) e a mediana é robusta a esses valores extremos.

A coluna `Blood Group` era a única variável categórica textual. Foi convertida com `LabelEncoder`, que atribui um número inteiro para cada categoria. Como o tipo sanguíneo não tem ordem natural, qualquer codificação numérica é equivalente para os algoritmos utilizados.

Após a limpeza, o dataset ficou com 42 colunas e zero valores ausentes.

---

## 5. Feature Engineering

Uma das decisões que mais impactou os resultados foi a criação de variáveis derivadas com base no conhecimento clínico da SOP. Em vez de entregar ao modelo apenas as variáveis brutas, procuramos criar features que representam os critérios diagnósticos e os padrões que a própria EDA revelou.

**Total de folículos** (`total_foliculos`): soma dos folículos do ovário esquerdo e direito. O critério de Rotterdam considera a contagem total — faz mais sentido clínico do que tratar cada ovário separadamente para fins de triagem. Essa feature ficou com correlação de 0,66 com o diagnóstico, superando as duas colunas originais separadas (0,60 e 0,65).

**Soma de sintomas** (`soma_sintomas`): soma de cinco variáveis binárias de sintomas — ganho de peso, crescimento de pelos, escurecimento de pele, queda de cabelo e acne. A ideia é capturar a "carga sintomática": uma paciente com quatro ou cinco desses sintomas tem um perfil muito diferente de uma com zero, mesmo que individualmente cada sintoma seja binário. Correlação de 0,58.

**Faixa de IMC** (`faixa_imc`): categorização do IMC nas faixas da OMS (abaixo do peso, normal, sobrepeso, obesidade, obesidade severa). O IMC contínuo não captura os limiares que têm significado clínico — a diferença entre 24,9 e 25,0 kg/m² é biologicamente relevante porque 25 é o limiar do sobrepeso.

**Razão LH/FSH** (`razao_lh_fsh`): a literatura médica define que uma razão LH/FSH acima de 2 é indicativa de SOP. O dataset já tinha FSH/LH (razão inversa) — criamos também a direta para deixar ambas disponíveis ao modelo.

Além da criação de features, foi feita uma seleção baseada em correlação com o target. Features com correlação absoluta menor que 0,05 foram removidas — entre elas pressão arterial, frequência respiratória, tipo sanguíneo, beta-HCG e TSH. Isso reduziu o espaço de features de 45 para 31, diminuindo o ruído e o risco de overfitting.

---

## 6. Modelos utilizados e justificativas

Foram treinados quatro modelos de classificação supervisionada:

**Regressão Logística** foi o ponto de partida natural. É um modelo interpretável, amplamente utilizado em contextos clínicos, e serve como baseline sólido para comparação. Usa uma função sigmoide para estimar a probabilidade de SOP dado o conjunto de features da paciente. O parâmetro `class_weight='balanced'` foi aplicado em todos os modelos para compensar o desequilíbrio de classes.

**Árvore de Decisão** foi incluída por sua característica de produzir regras explícitas do tipo IF/ELSE — o que facilita muito a explicação para um profissional de saúde. Um médico consegue entender e questionar "o modelo classificou como SOP porque a contagem de folículos foi maior que X e o AMH foi maior que Y", o que não acontece com modelos mais complexos.

**Random Forest** é um ensemble de múltiplas árvores de decisão com votação majoritária. É mais robusto que uma única árvore porque reduz a variância — cada árvore vê uma amostra diferente dos dados e um subconjunto diferente de features. Além disso, o Random Forest fornece a importância de cada feature naturalmente, o que é valioso para explicabilidade.

**KNN (K-Nearest Neighbors)** foi adicionado por representar uma lógica diferente dos demais: em vez de aprender uma função matemática, ele classifica uma paciente com base nas k pacientes mais parecidas no conjunto de treino. A intuição clínica é direta — pacientes com perfis laboratoriais similares tendem a ter diagnósticos similares. O melhor valor de k foi determinado por busca com validação cruzada: k=5 produziu F1 médio de 82,44% no conjunto de treino.

A normalização com `StandardScaler` foi aplicada antes de todos os modelos, mas é especialmente crítica para o KNN, que calcula distâncias euclidianas — sem normalização, features com escalas maiores dominariam o cálculo.

---

## 7. Resultados e interpretação

### Métricas no conjunto de teste

| Modelo               | Acurácia | Recall  | F1-Score | AUC-ROC |
|----------------------|----------|---------|----------|---------|
| Regressão Logística  | 89,91%   | **88,89%** | 85,33%   | **0,9631** |
| Árvore de Decisão    | 86,24%   | 80,56%  | 79,45%   | 0,8701  |
| Random Forest        | **93,58%** | 83,33% | **89,55%** | 0,9505  |
| KNN (k=5)            | 90,83%   | 77,78%  | 84,85%   | 0,9614  |

**Por que o Recall é a métrica mais importante aqui?**

Em diagnóstico médico, os erros não têm o mesmo custo. Um falso negativo — classificar como saudável uma paciente que tem SOP — significa que ela vai embora sem diagnóstico, sem tratamento, e pode desenvolver diabetes tipo 2, infertilidade e outras complicações nos anos seguintes. Um falso positivo — indicar suspeita de SOP em uma paciente saudável — vai gerar mais exames e possivelmente ansiedade, mas o erro é detectável e corrigível.

Por esse motivo, o Recall (que mede exatamente a taxa de casos positivos corretamente identificados) é a métrica prioritária nesse contexto.

A **Regressão Logística** foi o modelo com melhor Recall: identificou corretamente 88,89% das pacientes com SOP no conjunto de teste, com AUC de 0,963. O **Random Forest** teve o melhor F1-Score e acurácia, mas com Recall ligeiramente inferior (83,33%).

### Validação cruzada (K-Fold, k=5)

Para confirmar que os resultados não são artefato da divisão treino/teste, foi feita validação cruzada com 5 folds. Os resultados ficaram consistentes: Random Forest com F1 médio de 82,31% (±3,38%) e Regressão Logística com 80,34% (±4,79%). O desvio padrão baixo indica que os modelos generalizam bem para diferentes subconjuntos dos dados.

### Feature Importance e SHAP

A análise de importância das features pelo Random Forest confirmou que as variáveis criadas no Feature Engineering foram relevantes: `total_foliculos` ficou em **primeiro lugar** com 18,2% de importância, e `soma_sintomas` em **terceiro lugar** com 10,3%. Isso sugere que combinar variáveis relacionadas ao mesmo critério diagnóstico realmente ajudou o modelo.

O SHAP (SHapley Additive exPlanations) foi utilizado para explicar não apenas o comportamento global do modelo, mas também previsões individuais. O summary plot mostra que valores altos de `total_foliculos` e `soma_sintomas` empurram fortemente a previsão para SOP, enquanto ciclos regulares e AMH baixo empurram para o lado contrário. Esse nível de explicabilidade é o que permite que um médico questione e valide a sugestão do modelo antes de agir.

---

## 8. Discussão crítica

Os resultados obtidos são encorajadores para uma aplicação real, mas precisam ser contextualizados com as limitações do estudo.

**O que funciona bem:** os modelos capturaram padrões que têm respaldo clínico. As features mais importantes são exatamente as que a literatura médica coloca como centrais no diagnóstico de SOP — contagem de folículos, AMH, sintomas hiperandrogênicos. Isso dá confiança de que o modelo está aprendendo algo real, não apenas memorizando ruído.

**Limitação principal — tamanho do dataset:** 541 pacientes é um número razoável para um estudo piloto, mas pequeno para um sistema que seria implantado em produção. Idealmente, queríamos treinar com dezenas de milhares de casos de populações diversas.

**Origem geográfica restrita:** todos os dados vêm de Kerala, Índia. Características genéticas, dietéticas e de estilo de vida influenciam tanto a prevalência quanto a apresentação clínica da SOP. Um modelo treinado nessa população pode não generalizar bem para mulheres de outras etnias e regiões.

**Dependência de dados de ultrassom:** as features mais importantes (contagem de folículos) vêm da ultrassonografia. A qualidade dessas medidas varia com o equipamento e o operador — o que pode introduzir inconsistências se o modelo for implantado em unidades com equipamentos diferentes dos usados na coleta dos dados originais.

**Validação prospectiva:** o modelo foi avaliado em dados históricos. O teste real seria aplicá-lo em novos pacientes em tempo real, com acompanhamento do diagnóstico final para medir o desempenho real — algo que esse estudo não foi capaz de fazer.

**Como usar na prática:** o modelo mais indicado para triagem seria a Regressão Logística pelo maior Recall, com o Random Forest como complemento para entender quais variáveis pesaram mais em cada caso. A recomendação seria utilizá-lo como uma flag automática no prontuário eletrônico — quando o sistema detecta alto risco, sinaliza para o médico que vale aprofundar a investigação. O diagnóstico final sempre permanece com o profissional de saúde.

