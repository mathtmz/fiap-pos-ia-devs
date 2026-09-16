# Registro técnico de implementação — Fase 3

Atualizado em 15/09/2026. Para o estado consolidado, consulte o [contexto da Fase 3](./CONTEXTO_FASE3_IA_GENERATIVA.md), o [relatório técnico](./docs/RELATORIO_TECNICO.md), o [README](./README.md) e o [roteiro do vídeo](./docs/ROTEIRO_VIDEO.md).

## Decisões de implementação

- O projeto é um protótipo acadêmico com registros e instruções sintéticos, notas internas de demonstração e resumos parafraseados de fontes institucionais. Materiais didáticos de notícias e Project Gutenberg não entram no corpus médico ou no treinamento.
- Pedidos de hipótese diagnóstica, prescrição ou dose seguem para análise como solicitações de apoio à revisão médica. Sem fontes locais clinicamente validadas para uso individual, o sistema explicita a limitação e não formula a conclusão solicitada.
- O recuperador é lexical. As citações devem pertencer às fontes recuperadas; respostas sem citação são descartadas e podem seguir para `grounded_fallback` determinístico.
- As consultas SQLite usam parâmetros. A auditoria registra execução, etapa, decisão, fontes e latência, sem armazenar pergunta ou ID do paciente.
- Testes automatizados usam gerador falso/fallback. O smoke test do modelo com o adaptador é executado separadamente.

## Estado validado

O ajuste QLoRA de Qwen2.5-0.5B-Instruct foi concluído no Colab e o adaptador está em `code/outputs/lora_adapter`. A comparação de geração está em `code/outputs/metrics/generation_comparison.jsonl`, com 90 perguntas em três condições. O arquivo `code/outputs/metrics/avaliacao_assistida_ia.json` contém uma análise exploratória por rubrica das 270 respostas. A planilha separa essa análise de uma aba opcional para revisão manual, que pode complementar os resultados; tal revisão não é exigência expressa do enunciado.

O modelo e o adaptador foram carregados localmente em CPU. Quando a saída não apresentou citação rastreável, o validador a descartou e acionou `grounded_fallback`. Na consolidação mais recente, os 48 testes passaram e as métricas de recuperação foram atualizadas sobre 44 casos. O roteiro está pronto; a gravação e a conferência do vídeo de até 15 minutos ficam a cargo da equipe.

## Ambiente

O projeto foi executado localmente em Windows e no Google Colab. Os primeiros problemas de dependências e compatibilidade do Colab foram corrigidos; os detalhes de reprodução e limitações vigentes estão no README e no relatório técnico. Recomenda-se Python 3.12 para nova instalação.
