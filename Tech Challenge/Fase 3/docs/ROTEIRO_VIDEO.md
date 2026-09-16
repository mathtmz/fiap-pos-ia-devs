# Roteiro de demonstração — duração estimada: 11 a 12 minutos

## Preparação

1. Abra o PowerShell em `Tech Challenge/Fase 3/code` e inicie o app: `python -m streamlit run app.py`.
2. Deixe o navegador aberto na página inicial e o terminal disponível para exibir o comando de execução. Se o adaptador estiver carregado, aguarde a primeira inferência antes de iniciar a gravação.
3. Separe para a demonstração o registro `SYN-PCOS-01` e a pergunta: **“Quais são os limites da triagem e as pendências registradas?”**. Para segurança, use uma pergunta diagnóstica individual sem evidência validada, uma entrada com dado pessoal fictício e uma tentativa simples de prompt injection.
4. Abra também `outputs/lora_adapter/training_summary.json`, `outputs/metrics/retrieval_metrics.json` e `outputs/metrics/generation_comparison.jsonl` para apresentar evidências do treinamento e da avaliação.

## Sequência e fala sugerida

| Tempo | O que mostrar | Narração sugerida |
|---:|---|---|
| 0:00–0:40 | Título do projeto e README | “Este projeto demonstra um assistente de apoio à triagem sobre SOP/PCOS. A proposta é combinar um modelo ajustado, registros estruturados, recuperação de fontes e controles para apoiar a revisão médica.” |
| 0:40–1:30 | Enunciado e arquitetura no relatório | “O fluxo usa LangGraph para coordenar validação, consulta ao SQLite, recuperação, geração, verificação de citações e auditoria. O LangChain encapsula o modelo local e o contexto da consulta.” |
| 1:30–2:45 | Notebook do Colab e `training_summary.json` | “O Qwen 2.5 0.5B-Instruct foi ajustado com QLoRA em GPU Tesla T4, durante duas épocas. O conjunto tem 600 exemplos sintéticos: 420 para treino, 90 para validação e 90 para teste. As perdas registradas são métricas de otimização, não avaliação clínica.” |
| 2:45–5:15 | App: selecionar registro e enviar a pergunta preparada | “O aplicativo consulta os relatos e as pendências do registro no SQLite. As fontes aparecem separadas da resposta e podem ser abertas para rastrear a origem. O exemplo clínico está apresentado como rascunho e exige revisão do médico responsável.” |
| 5:15–6:30 | Abrir o trace do LangGraph e destacar a rota usada | “O trace expõe as etapas executadas. Neste caso, quando a geração não retorna uma citação recuperada válida, o validador descarta o texto e encaminha a execução para `grounded_fallback`, que produz um resumo determinístico com fonte.” |
| 6:30–8:00 | Fazer uma pergunta individual sobre diagnóstico, prescrição ou dose | “O sistema recebe esse tipo de solicitação como pedido de apoio, mas as fontes locais não estão validadas para sustentar uma conclusão individual. Por isso, o fluxo explicita a limitação e se abstém. A decisão final permanece com o médico responsável.” |
| 8:00–9:00 | Demonstrar bloqueio de dado identificável e prompt injection | “A validação ocorre antes da consulta ao registro. Entradas com informação pessoal identificável ou tentativa de alterar as regras são recusadas e não seguem para geração.” |
| 9:00–10:00 | Abrir `audit.jsonl` e mostrar campos sanitizados | “A auditoria registra a execução, os nós, a decisão, as fontes e a latência. A pergunta e o identificador do paciente não são armazenados.” |
| 10:00–11:15 | Apresentar métricas de recuperação e comparação | “Em 44 perguntas, Precision@3 foi 0,326, Recall@3 foi 0,943 e MRR foi 0,879. A comparação de geração reúne 90 perguntas em três condições. As respostas LoRA tiveram poucas citações válidas; os escores de rubrica são exploratórios e não demonstram segurança ou benefício clínico.” |
| 11:15–12:00 | Relatório técnico e conclusão | “O protótipo demonstra ajuste, integração com base estruturada, orquestração, controles e rastreabilidade. Os limites incluem corpus pequeno, dados sintéticos, recuperação lexical e a necessidade de avaliação profissional antes de qualquer uso clínico.” |

## Checklist de gravação

- [x] Treinamento QLoRA concluído e resumo de configuração/perdas salvo.
- [x] Adaptador instalado em `code/outputs/lora_adapter` e inferência local verificada.
- [x] Código modular, instruções de execução e notebook de treinamento incluídos no repositório.
- [x] Fluxo LangChain/LangGraph, consulta parametrizada ao SQLite, fontes e auditoria implementados.
- [x] Testes automatizados: 48 aprovados na execução local consolidada.
- [x] Recuperação reavaliada em 44 casos; comparação de geração e análise exploratória das 270 respostas registradas.
- [ ] Iniciar o app e confirmar antes da captura que as telas e os artefatos indicados estão disponíveis.
- [ ] Gravar, assistir à gravação e confirmar duração inferior a 15 minutos, áudio inteligível e dados de demonstração legíveis.

## Observações para a apresentação

- Identifique os dados e exemplos como sintéticos no contexto acadêmico; não os apresente como prontuários de pacientes reais.
- Diferencie a resposta gerada pelo Qwen da rota determinística `grounded_fallback` sempre que o trace mostrar essa substituição.
- Não interprete perdas, métricas de recuperação ou escores de rubrica como validação clínica.
- A revisão manual complementar das 270 respostas pode ser feita futuramente; ela não é requisito explícito no enunciado e não deve ser apresentada como concluída.

**Estado:** roteiro pronto para uso. Este arquivo não representa a gravação; o vídeo de até 15 minutos é a entrega restante que depende de captura e conferência pela equipe.
