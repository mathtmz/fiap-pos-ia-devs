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

### Resumo Clínico
O modelo de *Random Forest* classificou a paciente com um risco estimado de 4,0% para Síndrome dos Ovários Policísticos (SOP), indicando uma baixa probabilidade de presença da condição com base nos dados fornecidos. O resultado sugere que os parâmetros morfológicos ovarianos e a sintomatologia apresentada não se alinham ao padrão estatístico de pacientes diagnosticadas com SOP pelo modelo.

### Fatores Principais de Atenção
*   **Contagem de Folículos (Direito e Esquerdo):** O modelo atribui alto peso à contagem folicular. Valores dentro da normalidade fisiológica são os principais responsáveis pela redução da probabilidade de SOP.
*   **Soma de Sintomas e Hirsutismo:** A ausência ou baixa pontuação nestes indicadores clínicos reduz significativamente a predição de risco, visto que o modelo correlaciona a presença de sinais clínicos (como crescimento de pelos) com a classe positiva.

### Nível de Cautela e Métricas
O modelo apresenta um desempenho robusto, com **AUC-ROC de 0,95** e **acurácia de 92,6%**, indicando alta capacidade de discriminação entre casos positivos e negativos. No entanto, o **recall de 0,83** sugere que o modelo pode, ocasionalmente, não identificar casos positivos (falsos negativos). Portanto, o resultado deve ser interpretado com cautela, especialmente se houver forte suspeita clínica persistente.

### Limitações do Modelo
*   **Natureza Estatística:** O modelo identifica padrões em dados históricos e não substitui a avaliação clínica detalhada ou exames laboratoriais (como perfil hormonal).
*   **Variáveis Omitidas:** O modelo pode não considerar fatores como resistência à insulina, níveis de andrógenos séricos ou histórico familiar, que são cruciais para o diagnóstico clínico.
*   **Sensibilidade:** O *recall* de 83% indica que existe uma margem de erro onde a condição pode estar presente, mesmo com uma predição de baixo risco.

### Recomendação de Uso Seguro
Este resultado deve ser utilizado exclusivamente como uma ferramenta de apoio à triagem clínica. **A decisão final sobre o diagnóstico e a conduta terapêutica é de responsabilidade exclusiva de um profissional de saúde qualificado.** Recomenda-se que, independentemente deste resultado, a paciente consulte um ginecologista ou endocrinologista para uma avaliação completa, especialmente se apresentar sintomas clínicos ou irregularidades menstruais.

## Checagem de seguranca

{'mentions_triage_support': True, 'avoids_forbidden_terms': True, 'mentions_professional': True}
