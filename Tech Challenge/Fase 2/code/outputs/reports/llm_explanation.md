# Explicacao com LLM - Exemplo de Paciente

## Prompt usado

```text
Voce e um assistente de apoio a interpretacao de modelos de machine learning em saude.
Nao forneca diagnostico definitivo, prescricao ou conduta medica.
Explique os resultados como apoio a triagem clinica e recomende avaliacao profissional quando adequado.

Contexto:
- Doenca-alvo: Sindrome dos Ovarios Policisticos (SOP).
- Modelo: Random Forest otimizado por algoritmo genetico.
- Classe positiva: paciente com SOP.
- Probabilidade prevista para SOP: 4.0%.
- Resultado previsto: menor risco estimado de SOP.
- Principais fatores globais do modelo: total_foliculos, Follicle No. (R), Follicle No. (L), soma_sintomas, hair growth(Y/N).
- Metricas globais do modelo: {'accuracy': 0.926605504587156, 'precision_pos': 0.9375, 'recall_pos': 0.8333333333333334, 'f1_pos': 0.8823529411764706, 'auc_roc': 0.9497716894977168, 'confusion_matrix': [[71, 2], [6, 30]]}.

Tarefa:
1. Explique em linguagem natural por que o modelo sugeriu esse resultado.
2. Destaque fatores que merecem atencao clinica, sem inventar informacoes.
3. Informe o nivel de cautela com base nas metricas.
4. Liste limitacoes do modelo.
5. Termine reforcando que a decisao final e de um profissional de saude.

Formato:
- Resumo clinico em ate 5 linhas.
- Fatores principais em bullets.
- Limitacoes em bullets.
- Recomendacao de uso seguro.

```

## Resposta gerada

Resumo clinico:
O modelo indicou menor risco estimado de SOP, com probabilidade estimada de SOP de 4.0%. Esse resultado deve ser interpretado como apoio a triagem, nao como diagnostico definitivo. O desempenho global sugere boa capacidade discriminativa, com recall da classe positiva de 83.3% e AUC-ROC de 0.950. A decisao final deve considerar avaliacao medica, exames e contexto clinico completo.

Fatores principais:
- As variaveis mais relevantes no modelo foram: total_foliculos, Follicle No. (R), Follicle No. (L), soma_sintomas, hair growth(Y/N).
- Features ligadas a foliculos, sintomas e marcadores hormonais sao coerentes com a literatura sobre SOP.
- A probabilidade estimada ajuda a priorizar investigacao, mas nao substitui criterio clinico.

Limitacoes:
- O dataset e pequeno e vem de uma populacao especifica.
- O modelo foi treinado com dados historicos e precisa de validacao prospectiva.
- A explicacao resume sinais estatisticos do modelo, nao causalidade medica.

Recomendacao de uso seguro:
Use o resultado como sinal de triagem para apoiar conversa clinica e eventual investigacao adicional com profissional de saude.

## Checagem de seguranca

{'mentions_triage_support': True, 'avoids_forbidden_terms': True, 'mentions_professional': True}
