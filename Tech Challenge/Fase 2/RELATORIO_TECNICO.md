# Relatorio Tecnico - Tech Challenge Fase 2

**FIAP POSTECH - IA para Devs**
**Tema:** Otimizacao evolutiva e explicabilidade generativa para diagnostico assistido de SOP

## 1. Introducao

A Fase 2 evolui o projeto desenvolvido na Fase 1, cujo objetivo era criar um sistema de apoio ao diagnostico de Sindrome dos Ovarios Policisticos (SOP) usando modelos supervisionados. A proposta atual segue o Projeto 1 do Tech Challenge: otimizar modelos de diagnostico com algoritmos geneticos e integrar uma LLM para gerar explicacoes em linguagem natural.

O objetivo continua sendo triagem e apoio a decisao. O sistema nao substitui avaliacao medica, nao emite diagnostico definitivo e nao recomenda tratamento. Essa restricao e importante porque o dominio envolve saude, dados clinicos e risco de interpretacao indevida.

## 2. Dataset e baseline

Foi mantido o dataset PCOS usado na Fase 1, com 541 pacientes e variaveis clinicas, hormonais, sintomas e dados de ultrassom. A variavel alvo e `PCOS (Y/N)`, em que 1 representa paciente com SOP.

O pipeline herdado foi reproduzido em codigo modular:

- limpeza de identificadores e coluna vazia;
- conversao de colunas hormonais com tipos mistos;
- imputacao por mediana;
- codificacao de coluna textual;
- feature engineering clinico;
- selecao por correlacao;
- split estratificado;
- normalizacao com `StandardScaler`.

As features criadas na Fase 1 foram preservadas:

- `total_foliculos`;
- `soma_sintomas`;
- `faixa_imc`;
- `razao_lh_fsh`.

Resultados reproduzidos no conjunto de teste:

| Modelo | Accuracy | Precision SOP | Recall SOP | F1 SOP | AUC-ROC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Regressao Logistica | 89.91% | 82.05% | 88.89% | 85.33% | 96.31% |
| Arvore de Decisao | 86.24% | 78.38% | 80.56% | 79.45% | 87.01% |
| Random Forest | 93.58% | 96.77% | 83.33% | 89.55% | 95.05% |
| KNN | 90.83% | 93.33% | 77.78% | 84.85% | 96.14% |

Como se trata de triagem medica, o recall da classe positiva continua sendo a metrica mais sensivel: falso negativo significa deixar de sinalizar uma paciente com possivel SOP.

## 3. Algoritmo genetico

O algoritmo genetico foi implementado de forma explicita, para demonstrar os conceitos das aulas:

- individuo: conjunto de hiperparametros do modelo;
- gene: um hiperparametro especifico;
- populacao: conjunto de configuracoes candidatas;
- fitness: qualidade da configuracao;
- selecao: torneio com `k=3`;
- crossover: uniforme por gene;
- mutacao: troca do valor dentro do dominio permitido;
- elitismo: preservacao dos melhores individuos;
- hotstart: inclusao de configuracao conhecida do baseline na populacao inicial.

O modelo otimizado foi o Random Forest, por ter sido o melhor baseline geral da Fase 1. Os genes usados foram:

| Gene | Dominio |
| --- | --- |
| `n_estimators` | 50, 100, 150, 200, 300, 500 |
| `max_depth` | None, 3, 5, 8, 12, 16, 24, 32 |
| `min_samples_split` | 2, 4, 6, 8, 10, 15, 20 |
| `min_samples_leaf` | 1, 2, 3, 4, 5, 8, 10 |
| `max_features` | sqrt, log2, None |
| `class_weight` | balanced, balanced_subsample, None |

A funcao de fitness priorizou recall, sem ignorar F1, AUC e acuracia:

```text
fitness = 0.50 * recall_pos
        + 0.30 * f1_pos
        + 0.15 * auc_roc
        + 0.05 * accuracy
        - penalidade_overfit
```

Essa escolha reflete o custo clinico maior do falso negativo.

## 4. Experimentos

Foram executadas tres configuracoes:

| Experimento | Populacao | Geracoes | Mutacao | Crossover | Objetivo |
| --- | ---: | ---: | ---: | ---: | --- |
| GA-Exploratorio | 20 | 20 | 0.25 | 0.80 | Explorar mais o espaco |
| GA-Balanceado | 30 | 30 | 0.15 | 0.75 | Equilibrar exploracao e refinamento |
| GA-Conservador | 20 | 40 | 0.08 | 0.65 | Refinar boas solucoes |

Melhor configuracao encontrada em validacao:

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

Na validacao interna do algoritmo genetico, essa configuracao atingiu:

- fitness: 0.9249;
- recall positivo: 91.43%;
- F1 positivo: 91.43%;
- AUC-ROC: 97.53%;
- accuracy: 94.44%.

No conjunto de teste final:

| Modelo | Accuracy | Precision SOP | Recall SOP | F1 SOP | AUC-ROC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Random Forest baseline | 93.58% | 96.77% | 83.33% | 89.55% | 95.05% |
| Random Forest otimizado por GA | 92.66% | 93.75% | 83.33% | 88.24% | 94.98% |

O resultado mostra que o algoritmo genetico encontrou uma configuracao forte na validacao, mas ela nao superou o baseline no teste final. Isso e tecnicamente relevante: em datasets pequenos, a busca de hiperparametros pode se ajustar ao conjunto de validacao sem ganho real em teste. A conclusao correta e discutir esse comportamento como evidencia de necessidade de validacao adicional e controle de overfitting.

## 5. Explicabilidade e LLM

A explicabilidade foi dividida em duas camadas.

A primeira camada e tecnica:

- feature importance do Random Forest;
- permutation importance;
- matriz de confusao;
- curva ROC;
- metricas comparativas.

A segunda camada usa LLM para transformar os resultados em linguagem natural. A LLM nao recebe a tarefa de diagnosticar; ela apenas explica o resultado do modelo, com restricoes claras no prompt:

- nao fornecer diagnostico definitivo;
- nao prescrever tratamento;
- indicar que o resultado e apoio a triagem;
- reforcar que a decisao final e de profissional de saude;
- mencionar limitacoes e incertezas.

Para manter a execucao local reproduzivel, foi implementado `LLM_PROVIDER=mock`. A estrutura permite troca futura por provider real via API, alinhada ao que foi visto nas aulas: treinar LLM do zero nao e viavel para este contexto; usar modelo pre-treinado com prompt engineering e controle de seguranca e o caminho adequado.

## 6. Monitoramento e arquitetura

O projeto registra:

- historico por geracao em JSONL;
- melhor fitness e fitness medio;
- diversidade da populacao;
- melhor cromossomo por geracao;
- metricas finais em CSV;
- modelo final em `joblib`;
- graficos em PNG.

Arquitetura alvo cloud-ready:

```text
Scripts/Notebook
  -> pipeline de dados
  -> treino baseline
  -> jobs de algoritmo genetico
  -> armazenamento de artefatos
  -> explicacao por LLM
  -> relatorio e monitoramento
```

Em uma implantacao real, os experimentos poderiam ser executados como jobs independentes em Vertex AI, Azure ML ou SageMaker, com storage para datasets/modelos e logs centralizados.

## 7. Testes

Foram criados testes automatizados para:

- preparacao dos dados e criacao das features;
- validade dos cromossomos;
- crossover e mutacao;
- funcao de fitness;
- construcao do prompt;
- resposta mock da LLM;
- checagem de seguranca contra texto prescritivo.

Resultado da suite:

```text
8 passed
```

## 8. Limitacoes

As principais limitacoes permanecem:

- dataset pequeno, com 541 pacientes;
- origem geografica restrita;
- dados historicos, sem validacao prospectiva;
- risco de overfitting em otimizacao de hiperparametros;
- dependencia de medidas de ultrassom;
- LLM pode gerar texto inadequado se nao houver prompt e avaliacao de seguranca;
- o sistema e apoio a triagem, nao ferramenta de diagnostico autonomo.

## 9. Conclusao

A Fase 2 transformou o trabalho da Fase 1 em um projeto mais completo de experimentacao em IA. O algoritmo genetico foi implementado com os operadores estudados nas aulas e produziu uma configuracao competitiva, embora sem superar o melhor baseline no teste final. Esse resultado reforca uma discussao importante em ciencia de dados: melhorar validacao nao garante ganho de generalizacao.

A integracao com LLM agregou valor na camada de interpretabilidade, desde que usada com restricoes claras e sem substituir julgamento medico. O projeto ficou mais reprodutivel, testavel e alinhado aos topicos da fase: algoritmos geneticos, PLN/LLMs, IA generativa, logging, avaliacao e arquitetura preparada para cloud.
