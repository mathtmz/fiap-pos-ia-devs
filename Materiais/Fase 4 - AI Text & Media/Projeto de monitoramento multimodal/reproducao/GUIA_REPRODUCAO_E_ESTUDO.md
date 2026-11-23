# Guia de estudo e reprodução

Este guia organiza o trabalho em três percursos: aprender e executar cada etapa, apresentar o mesmo fluxo em vídeo e permitir uma reprodução independente a partir do Git. O [README da Fase 4](../../../../Tech%20Challenge/Fase%204/README.md) é o ponto de entrada; este documento explica o que cada comando faz e onde ficam as evidências.

## 1. Mapa do trabalho

| Parte | Responsabilidade | Evidência principal |
|---|---|---|
| `code/src/fisio_fase4/` | Análises, regras, eventos, fusão e reprodução temporal | Código Python documentado |
| `code/app.py` | Interface para carregar dados, processar o caso e acompanhar alertas | Demonstração Streamlit |
| `code/scripts/` | Preparar ambiente, obter fontes, avaliar modelos e reproduzir o fluxo | Comandos de execução reproduzíveis |
| `data/synthetic/` | Casos artificiais e rótulos de teste mantidos no Git | CSVs e conjunto de frases fixas |
| `FONTES_DADOS.md` | Manifesto das fontes e materiais externos | URLs, licenças, versões, trechos e instruções |
| `docs/resultados/` | Métricas, logs e artefatos autorais usados no relatório | JSON, JSONL e vídeos anotados curtos |

Vídeos, áudios, anotações de terceiros e pesos já hospedados externamente são obtidos pelos links do manifesto e não duplicados no Git. `data/public/` e `code/outputs/` são locais, ignorados pelo Git, para downloads e arquivos temporários. Os resultados finais e os exemplos anotados usados no relatório ficam em `docs/resultados/`.

## 2. Ambiente do zero

### Pré-requisitos

- Python 3.12.
- Internet para instalar dependências e baixar fontes/modelos.
- Espaço em disco: a avaliação visual completa baixa cerca de 0,92 GiB de vídeos, além de pesos e dependências.
- Nenhuma chave de API ou segredo é necessário.

### Instalação

Na raiz `Tech Challenge/Fase 4`, execute:

```bash
python3.12 code/scripts/setup_environment.py
```

No Windows, use o lançador Python correspondente:

```powershell
py -3.12 code/scripts/setup_environment.py
```

O script cria `.venv`, instala as versões fixadas em `code/requirements.txt`, disponibiliza FFmpeg para o Whisper e verifica o ambiente. Ative o ambiente antes dos comandos seguintes:

```bash
source .venv/bin/activate
```

```powershell
.venv\Scripts\Activate.ps1
```

Valide a instalação sem baixar dados ou modelos:

```bash
python code/scripts/check_environment.py
python -m pytest code/tests -q
```

### Reprodução rápida

```bash
python code/scripts/reproduce.py --quick
```

Esse percurso testa o ambiente e os componentes que não exigem modelos pesados, executa os testes automatizados e gera casos normal e anômalo somente com séries sintéticas. Os relatórios JSON resultantes são copiados para `docs/resultados/reproduction_quick_*.json`.

### Reprodução completa

```bash
python code/scripts/reproduce.py --full --accept-external-downloads
```

O percurso completo baixa os áudios sintéticos com transcrição de referência, as anotações e os cinco vídeos do exercício 1 do REHAB26-ViewAngles. Em seguida, obtém os pesos permitidos diretamente das fontes, compara Whisper, avalia Qwen, executa validação cruzada visual por participante, gera exemplos visuais anotados, processa um caso multimodal sintético e reproduz os alertas a 1×.

Esse comando pode demorar e exige aproximadamente 0,92 GiB para os vídeos REHAB26, além dos modelos. Os vídeos e pesos baixados ficam em diretórios ignorados pelo Git. Para executar as etapas separadamente, veja a lista abaixo e o [manifesto de fontes](../contexto/FONTES_DADOS.md).

## 3. Experimentos e resultados esperados

| Experimento | Comando principal | Resultado versionado |
|---|---|---|
| Whisper `tiny`, `base`, `small` | `python code/scripts/compare_whisper.py` | `docs/resultados/whisper_comparacao.json` |
| VAD ligado/desligado | `python code/scripts/evaluate_vad.py` | `docs/resultados/vad_comparacao.json` |
| Agrupamento de locutores | `python code/scripts/run_demo.py --audio data/public/consultas/OAW04_consultation.wav --normal --diarize --output code/outputs/diarizacao_experimental` e `python code/scripts/evaluate_diarization.py` | `docs/resultados/diarizacao_sintetica.json` |
| Extração textual Qwen | `python code/scripts/evaluate_text.py` | `docs/resultados/text_evaluation.json` |
| Visão com divisão por participante (0,5 quadro/s por padrão) | `python code/scripts/evaluate_rehab26.py` | `docs/resultados/rehab26_lopo.json` |
| Trechos visuais de demonstração | `python code/scripts/prepare_rehab26_examples.py` e `python code/scripts/generate_vision_evidence.py` | `docs/resultados/vision_examples/` |
| Caso normal | `python code/scripts/run_demo.py --normal --no-qwen --output code/outputs/normal` | Relatório copiado para `docs/resultados/reproduction_normal_case.json` no fluxo completo |
| Caso anômalo integrado | Executado pelo orquestrador `reproduce.py --full` | `docs/resultados/reproduction_anomaly_case.json` |
| Reprodução temporal dos alertas | `python code/scripts/replay_multimodal.py docs/resultados/reproduction_anomaly_case.json --speed 1 --output docs/resultados/replay_anomaly.jsonl` | Eventos ordenados e latência local em JSONL |

### Como interpretar as avaliações

- **Vídeo:** cada dobra retira uma pessoa inteira do ajuste e a usa no teste. Os limiares são calculados somente com as outras quatro. O relatório traz cobertura, trechos inconclusivos, métricas por erro, F1 macro e comparação binária com o baseline MediaPipe.
- **Áudio:** WER compara a transcrição automática com os roteiros sintéticos disponíveis. Tempo e memória são medidos em processos separados por modelo. Esses resultados não estimam desempenho em áudio clínico.
- **Texto:** 30 frases sintéticas fixas medem sentimento, termos, alertas e encaminhamento para revisão. Casos negados e interrogativos não devem se transformar automaticamente em alertas afirmativos.
- **Alertas:** os eventos mantêm modalidade, tempo, origem, regra/modelo e evidência. A reprodução mede a entrega local de eventos pré-calculados; não mede inferência contínua do vídeo ou áudio.

Os resultados medidos na reprodução completa foram: Whisper `small`, WER agregado 0% em duas consultas sintéticas (14,434 s); `base`, 6,76% (6,395 s); `tiny`, 9,46% (4,275 s). Na consulta OAW04, o WER com VAD foi 80,77%, contra 15,38% sem VAD. Qwen obteve F1 macro de sentimento 0,6067, F1 de encaminhamento de alertas 0,9231 e F1 de revisão humana 0,9000 em 30 frases fixas. A avaliação de diarização alinhou 78 palavras, com 100% de acurácia após escolher retrospectivamente o melhor mapeamento de dois grupos; não é DER. No REHAB26, OpenPose/YOLO teve F1 micro 0,7959 em 60 das 556 repetições (10,79% de cobertura), deixando 496 inconclusivas; MediaPipe cobriu 73,02%, com F1 micro 0,6538. Consulte `rehab26_lopo.json` antes de apresentar esses valores, inclusive a cobertura e os falsos positivos. As matrizes completas e os erros por amostra estão nos JSONs acima. Essas medidas são específicas dos dados e da execução, não indicadores clínicos.

### Processamento dos vídeos públicos de atendimento

Os links estão em [Fontes](../contexto/FONTES_DADOS.md). Obtenha os áudios localmente conforme a autorização da equipe e os termos da plataforma; a mídia não é copiada para o Git. Execute:

```bash
python code/scripts/process_public_consultations.py \
  --therapy-audio /caminho/terapia_manual.wav \
  --hip-audio /caminho/reabilitacao_quadril.wav
```

O script usa Whisper small, gera relatórios integrais locais em `code/outputs/` e atualiza `docs/resultados/consultas_publicas_resumo.json` sem incluir transcrições. Sem referência humana revisada, não calcula WER. Os resumos já versionados registram execuções anteriores, sem alegar revisão manual.

## 4. Percurso de estudo e explicação oral

1. Leia o enunciado e a matriz no [relatório final](../relatorios/RELATORIO_FINAL_ENTREGA.md).
2. Consulte a origem e licença de cada entrada em [Fontes](../contexto/FONTES_DADOS.md).
3. Execute a reprodução rápida e abra os relatórios JSON de sinais e prescrições sintéticos.
4. Execute as avaliações de Whisper, Qwen e vídeo; compare os resultados com os baselines anteriores.
5. Abra os exemplos anotados e localize em `rehab26_lopo.json` os erros detectados, não detectados e inconclusivos.
6. Rode a interface com os mesmos arquivos do caso anômalo e compare o resultado com o JSON gerado pelos scripts.
7. Explique que a associação de fontes distintas é artificial e que os modelos não têm validação clínica.

Para cada módulo, o grupo deve conseguir explicar: qual entrada recebe, qual transformação executa, qual regra/modelo gera o evento, onde está a evidência e o que o resultado não permite concluir.

## 5. Percurso de apresentação

O [roteiro do vídeo](../apresentacao/ROTEIRO_VIDEO.md) e o [guia de apresentação](../apresentacao/GUIA_APRESENTACAO.md) usam os mesmos casos e arquivos produzidos pela reprodução completa. Antes de gravar:

1. Execute a reprodução rápida para verificar o ambiente e os testes.
2. Execute a demonstração completa ou abra os artefatos versionados em `docs/resultados/vision_examples/`.
3. Mostre um exemplo de erro, outro normal, a linha do tempo, a origem de um alerta e a matriz de avaliação.
4. Indique explicitamente o que foi calculado antes da reprodução e onde os dados são sintéticos.
5. Grave até 15 minutos, publique no YouTube ou Vimeo e atualize o link no README e no relatório.

As mídias reais hospedadas em canais externos são apresentadas por link e timestamp. O repositório público mantém apenas resultados minimizados desses atendimentos, sem transcrições integrais.

## 6. Solução de problemas

- Se o ambiente detectar Python diferente de 3.12, invoque o inicializador com `python3.12` ou `py -3.12`.
- Se Whisper não encontrar FFmpeg, ative `.venv` e rode `python code/scripts/setup_ffmpeg.py`.
- Se uma fonte ou modelo estiver temporariamente indisponível, os links e comandos de obtenção estão no manifesto; resultados anteriormente produzidos permanecem consultáveis em `docs/resultados/`.
- A avaliação visual completa precisa dos cinco vídeos baixados. Se houver interrupção, repita o comando de obtenção; os arquivos completos existentes são reutilizados e o manifesto local registra seus checksums.
- `--quick` é a opção de verificação sem baixar os vídeos REHAB26 ou pesos de visão.
