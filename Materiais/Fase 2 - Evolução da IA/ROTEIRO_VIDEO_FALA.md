# Roteiro do vídeo — FALA (o que ler)

Tech Challenge Fase 2 — Projeto 1. Este arquivo contém apenas o texto a ser lido em cada
bloco. Os comandos e o que deve estar na tela estão em `ROTEIRO_VIDEO_TELA.md`, com as mesmas
seções e tempos.

---

## 1. Abertura (0:00 – 0:45)

"Este vídeo apresenta a Fase 2 do Tech Challenge, Projeto 1: otimização de modelos de
diagnóstico com algoritmos genéticos e integração com LLM. O projeto evolui o classificador
de Síndrome dos Ovários Policísticos desenvolvido na Fase 1, mantendo o mesmo dataset e
adicionando duas capacidades pedidas no desafio: otimização evolutiva de hiperparâmetros e
explicação dos resultados em linguagem natural via LLM."

---

## 2. Estrutura do projeto e execução (0:45 – 2:00)

"O projeto é um pacote Python modular, com ambiente virtual próprio, dependências fixadas em
`requirements.txt` e scripts separados por responsabilidade: preparação de dados, modelos,
algoritmo genético, avaliação, explicabilidade e integração com LLM. Toda a execução é local,
sem dependência de nuvem."

"Antes de qualquer coisa, a suíte de testes automatizados confirma que os componentes
principais — dados, algoritmo genético, tuning avançado e explicação por LLM — continuam
funcionando."

---

## 3. Baseline herdado da Fase 1 (2:00 – 3:00)

"Reproduzimos os quatro modelos da Fase 1 — Regressão Logística, Árvore de Decisão, Random
Forest e KNN — como ponto de comparação. O Random Forest foi o melhor baseline geral e é o
modelo escolhido para a otimização evolutiva. Como o objetivo é triagem médica, o recall da
classe positiva é a métrica mais sensível: falso negativo significa deixar de sinalizar uma
paciente com possível SOP."

---

## 4. Algoritmo genético (3:00 – 6:30)

"O algoritmo genético foi implementado com os conceitos vistos em aula: cada indivíduo é um
conjunto de hiperparâmetros do Random Forest — número de árvores, profundidade máxima, split
mínimo, entre outros. A seleção usa torneio, o cruzamento é uniforme por gene, há mutação
controlada por taxa, elitismo para preservar os melhores indivíduos, e um hotstart com a
configuração conhecida do baseline. A função de fitness prioriza recall, sem ignorar F1, AUC e
acurácia, com penalidade para overfitting entre treino e validação."

"Executamos três experimentos com configurações diferentes de população, gerações, mutação e
crossover — exploratório, balanceado e conservador — conforme pedido no desafio."

"O gráfico mostra a evolução do fitness ao longo das gerações. No conjunto de teste final, o
modelo otimizado pelo GA não superou o Random Forest baseline — um resultado que discutimos no
relatório: a busca evolutiva melhorou a validação, mas isso não garantiu ganho de
generalização, o que é uma discussão real em ciência de dados com datasets pequenos."

---

## 5. Escalabilidade automática e tracking (6:30 – 9:00)

"O desafio pede recursos de escalabilidade automática para variações de demanda, além de
monitoramento e logging. Baseamos essa interpretação no material da disciplina de ML na
Cloud: lá, escalabilidade aparece como jobs de treinamento em paralelo — sweep jobs com limite
de execuções concorrentes — e não como uma API de serving. Aplicamos essa mesma lógica de
forma local."

"Note que não passamos o número de workers: ele é calculado automaticamente a partir da
quantidade de jobs pendentes e dos núcleos de CPU disponíveis — o log mostra exatamente isso.
Cada job também grava métricas em MLflow local e mensagens de aplicação em
`outputs/logs/pipeline.log`."

*(Se abrir a UI do MLflow)*: "Aqui dá para ver a execução registrada no MLflow, com os
parâmetros do algoritmo genético, as métricas de validação e o log da geração como artefato —
tudo rodando localmente, sem servidor externo."

---

## 6. Tuning avançado (9:00 – 9:45)

"Como investigação adicional, testamos GA com validação cruzada, GA escolhendo entre dois
modelos, e calibração de threshold de decisão. O melhor resultado veio da calibração do
threshold do Random Forest para 0,60, elevando a acurácia e o F1 da classe positiva sem
reduzir o recall."

---

## 7. Integração com LLM (9:45 – 13:00)

"A segunda parte do desafio pede integração com LLM para interpretar os resultados. O prompt
inclui regras explícitas de segurança: não fornecer diagnóstico definitivo, não prescrever
tratamento, reforçar que a decisão final é do profissional de saúde. Implementamos três
providers — um mock local para demonstração reprodutível, e integrações reais com OpenAI e
Gemini."

"O relatório gerado mostra o prompt usado, a resposta da LLM e duas checagens automáticas: uma
de segurança — confirmando que a resposta evita linguagem prescritiva e menciona o
profissional de saúde — e uma de qualidade, que verifica se a probabilidade citada é
consistente com o modelo, se a resposta cobre a estrutura pedida no prompt e se menciona
fatores reais do modelo, não inventados."

*(Se mostrar uma execução real)*: "Também executamos uma chamada real com Gemini, com o mesmo
padrão de segurança e qualidade avaliado automaticamente."

---

## 8. Testes e arquitetura (13:00 – 14:15)

"Temos 25 testes automatizados cobrindo preparação de dados, operadores do algoritmo genético,
função de fitness, tuning avançado, prompt e respostas da LLM, avaliação de qualidade e
segurança, dimensionamento automático de workers e integração com MLflow."

"A arquitetura resume o fluxo: dados, baseline, grade de experimentos com workers
dimensionados automaticamente, tracking local em arquivos e MLflow, escolha do melhor modelo,
e explicação via LLM. Toda a execução acontece nesta máquina local."

---

## 9. Encerramento (14:15 – 15:00)

"Resumindo: implementamos o algoritmo genético completo com os operadores pedidos, comparamos
o modelo otimizado com o baseline de forma honesta — inclusive quando o GA não superou o
baseline —, tratamos escalabilidade e logging como execução de jobs de treinamento com
dimensionamento automático e tracking em MLflow, e integramos uma LLM para interpretar os
resultados com segurança e qualidade avaliadas automaticamente. Os detalhes de cada decisão
estão no relatório técnico e no README do repositório. Obrigado."
