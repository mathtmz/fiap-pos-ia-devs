# Passo a passo para reproduzir a Fase 4

Este documento descreve, em ordem, os comandos para preparar o ambiente, verificar a instalação, repetir os experimentos, abrir a demonstração e localizar os resultados. Cada comando deve ser executado a partir da pasta `Tech Challenge/Fase 4`, salvo quando indicado.

O projeto não requer chaves de API. A reprodução completa precisa de internet para instalar bibliotecas e obter materiais e pesos externos. A equipe informou que a instituição autorizou substituir Azure Speech e Azure Text Analytics por Whisper e Qwen executados localmente; o código não chama Azure.

> **Limite da reprodução:** o fluxo automatizado usa consultas sintéticas em português, vídeos de exercício públicos e dados sintéticos de sinais vitais e prescrições. Ele não baixa os vídeos públicos de consultas do YouTube. Para processar esses materiais, consulte a seção [Consultas públicas em português](#10-processar-as-consultas-públicas-em-português).

## Índice

1. [O que será reproduzido](#1-o-que-será-reproduzido)
2. [Requisitos](#2-requisitos)
3. [Obter o repositório e entrar na pasta](#3-obter-o-repositório-e-entrar-na-pasta)
4. [Criar o ambiente Python](#4-criar-o-ambiente-python)
5. [Verificar ambiente e executar o percurso rápido](#5-verificar-ambiente-e-executar-o-percurso-rápido)
6. [Executar a reprodução completa](#6-executar-a-reprodução-completa)
7. [Reexecutar uma etapa específica](#7-reexecutar-uma-etapa-específica)
8. [Reproduzir análises exploratórias do REHAB24-6](#8-reproduzir-análises-exploratórias-do-rehab24-6)
9. [Abrir a interface e simular a chegada de dados](#9-abrir-a-interface-e-simular-a-chegada-de-dados)
10. [Processar as consultas públicas em português](#10-processar-as-consultas-públicas-em-português)
11. [Conferir os resultados gerados](#11-conferir-os-resultados-gerados)
12. [Onde cada arquivo é armazenado](#12-onde-cada-arquivo-é-armazenado)
13. [Solução de problemas](#13-solução-de-problemas)

## 1. O que será reproduzido

O projeto percorre quatro grupos de análise:

- **Áudio e texto:** Whisper compara tamanhos de modelo em duas consultas sintéticas roteirizadas; Qwen analisa 30 frases sintéticas; há uma comparação do VAD e um ensaio exploratório de agrupamento de locutores.
- **Vídeo:** YOLOv8n e OpenPose analisam movimento; MediaPipe funciona como baseline. A avaliação principal usa 556 repetições anotadas do REHAB26-ViewAngles, com uma pessoa retida para teste em cada dobra.
- **Dados tabulares:** regras aplicadas a CSVs sintéticos detectam valores de sinais vitais e mudanças em prescrições.
- **Integração:** as evidências são reunidas por caso, transformadas em eventos e apresentadas em relatórios JSON e em uma reprodução temporal local.

Os materiais externos baixados ficam em pastas locais ignoradas pelo Git. O repositório contém código, dados sintéticos, instruções, manifestos, métricas e evidências produzidas pelo projeto. Consulte [FONTES.md](../contexto/FONTES_DADOS.md) antes de reutilizar fontes ou pesos.

## 2. Requisitos

- **Python 3.12**.
- **Git** para obter o repositório.
- Conexão com a internet para instalar dependências e, na reprodução completa, obter as fontes e os modelos.
- Espaço em disco: os cinco vídeos REHAB26 usados na avaliação visual somam aproximadamente **0,92 GiB**. Dependências, pesos Whisper, Qwen, YOLOv8 e OpenPose exigem espaço adicional.
- Terminal: Terminal no macOS/Linux, PowerShell no Windows ou Git Bash.

O script de instalação configura FFmpeg dentro do ambiente Python. Não é necessário instalar uma chave de serviço ou configurar credenciais Azure.

## 3. Obter o repositório e entrar na pasta

### Se ainda não tiver uma cópia local

Execute estes comandos em uma pasta onde queira guardar o projeto:

```bash
git clone https://github.com/mathtmz/fiap-pos-ia-devs.git
cd "fiap-pos-ia-devs/Tech Challenge/Fase 4"
```

`git clone` baixa o repositório. `cd` entra na pasta da Fase 4. No PowerShell, o mesmo caminho pode ser escrito assim:

```powershell
git clone https://github.com/mathtmz/fiap-pos-ia-devs.git
Set-Location "fiap-pos-ia-devs\Tech Challenge\Fase 4"
```

### Se o repositório já estiver no computador

Abra um terminal na raiz do repositório e entre na pasta da Fase 4:

```bash
cd "Tech Challenge/Fase 4"
```

No PowerShell:

```powershell
Set-Location "Tech Challenge\Fase 4"
```

Confirme que entrou no diretório correto:

```bash
pwd
```

O caminho exibido deve terminar em `Tech Challenge/Fase 4`. Os próximos comandos usam caminhos relativos a essa pasta.

## 4. Criar o ambiente Python

### 4.1 Confirmar a versão do Python

No macOS ou Linux:

```bash
python3.12 --version
```

No Windows:

```powershell
py -3.12 --version
```

A saída deve informar Python 3.12. O projeto fixa suas dependências para essa versão. Se o comando não existir, instale Python 3.12 por uma fonte oficial para seu sistema operacional antes de continuar.

### 4.2 Instalar dependências e configurar FFmpeg

No macOS ou Linux:

```bash
python3.12 code/scripts/setup_environment.py
```

No Windows:

```powershell
py -3.12 code/scripts/setup_environment.py
```

O script faz o seguinte:

1. Confere que está usando Python 3.12.
2. Cria o ambiente isolado `.venv` se ele ainda não existir.
3. Instala as versões fixadas em `code/requirements.txt`.
4. Disponibiliza FFmpeg no ambiente para o Whisper.
5. Verifica se as dependências e versões esperadas estão disponíveis.

A instalação pode levar alguns minutos. O ambiente virtual não é versionado no Git.

### 4.3 Ativar o ambiente

No macOS ou Linux:

```bash
source .venv/bin/activate
```

No PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

No Git Bash para Windows:

```bash
source .venv/Scripts/activate
```

Depois de ativar, o início do prompt normalmente exibe `(.venv)`. Mantenha o ambiente ativado nas próximas etapas. Se abrir outro terminal, ative-o novamente.

Para sair do ambiente ao terminar:

```bash
deactivate
```

## 5. Verificar o ambiente e executar o percurso rápido

### 5.1 Verificação explícita (opcional)

```bash
python code/scripts/check_environment.py
```

Confere Python, versões instaladas e disponibilidade do FFmpeg. O comando não baixa os vídeos REHAB26 nem os pesos de visão.

Para rodar os testes diretamente:

```bash
python -m pytest code/tests -q
```

Executa os testes automatizados e resume os resultados no terminal. O percurso rápido também executa essa verificação e os testes, então é possível pular esses dois comandos e ir direto ao próximo.

### 5.2 Reprodução rápida

```bash
python code/scripts/reproduce.py --quick
```

Esse é o primeiro percurso recomendado. O script verifica o ambiente, executa os testes e gera casos sintéticos normal e anômalo. Não baixa os vídeos REHAB26 nem executa as avaliações visuais pesadas.

Os relatórios ficam em:

- `docs/resultados/reproduction_quick_normal.json`
- `docs/resultados/reproduction_quick_anomaly.json`

O cenário normal deve terminar sem eventos. O cenário anômalo demonstra regras em sinais vitais e prescrições sintéticos. Não interprete os valores como limites clínicos.

## 6. Executar a reprodução completa

Antes de iniciar, confirme internet e espaço em disco. O processo pode demorar porque baixa os vídeos de avaliação, os modelos OpenPose e YOLOv8 e, na primeira utilização, pesos Whisper e Qwen.

Execute:

```bash
python code/scripts/reproduce.py --full --accept-external-downloads
```

O argumento `--full` seleciona a sequência completa. O argumento `--accept-external-downloads` confirma que você aceita baixar aproximadamente 0,92 GiB de vídeos REHAB26, além dos pesos dos modelos. Sem esse argumento, o script interrompe a execução antes de baixar os vídeos.

### 6.1 O que o comando completo executa

O script executa as etapas abaixo em ordem. Você não precisa repetir os comandos desta tabela se já concluiu `reproduce.py --full`; a tabela explica o que foi feito e serve para reexecutar partes específicas.

| Ordem | Comando executado pelo fluxo completo | O que faz |
|---:|---|---|
| 1 | `python code/scripts/download_consultas_rehab26.py --video --participants all` | Baixa as consultas **sintéticas** OAW01/OAW04 com referências, os arquivos de anotações REHAB26 e os vídeos dos cinco participantes. Gera manifesto local com tamanhos e hashes. |
| 2 | `python code/scripts/setup_vision_models.py` | Obtém pesos OpenPose e YOLOv8n, verifica os arquivos e registra suas fontes e hashes. |
| 3 | `python code/scripts/compare_whisper.py` | Compara Whisper `tiny`, `base` e `small` com as mesmas duas transcrições sintéticas de referência. |
| 4 | `python code/scripts/run_demo.py --audio data/public/consultas/OAW04_consultation.wav --normal --diarize --output code/outputs/diarizacao_experimental --case-id oaw04_diarizacao` | Faz um ensaio exploratório de agrupamento de locutores na consulta sintética OAW04; não atribui automaticamente os papéis de paciente e profissional. |
| 5 | `python code/scripts/evaluate_diarization.py` | Compara os grupos de locutor com a referência sintética e salva a métrica exploratória. |
| 6 | `python code/scripts/evaluate_vad.py` | Compara a transcrição de OAW04 com e sem VAD. |
| 7 | `python code/scripts/evaluate_text.py` | Avalia sentimento, termos, alertas e encaminhamento para revisão em 30 frases sintéticas usando Qwen. |
| 8 | `python code/scripts/evaluate_rehab26.py --sample-fps 0.5` | Executa a validação visual leave-one-participant-out em 556 repetições, amostrando 0,5 quadro por segundo. |
| 9 | `python code/scripts/prepare_rehab26_examples.py` | Prepara clipes curtos para demonstração a partir das anotações REHAB26. |
| 10 | `python code/scripts/generate_vision_evidence.py --sample-fps 5` | Produz exemplos visuais anotados e um índice compacto em `docs/resultados/vision_examples/`. |
| 11 | `python code/scripts/prepare_audio_demo.py` | Cria uma cópia desacelerada da consulta OAW04 sintética para demonstrar uma regra acústica; não é dado clínico. |
| 12 | `python code/scripts/run_demo.py --normal --no-qwen --output code/outputs/reproduction/full/normal` | Processa o caso normal com os CSVs sintéticos de sinais vitais e prescrições. |
| 13 | `python code/scripts/run_demo.py --video data/public/rehab26/demo_clips/low_abduction.mp4 --audio data/public/consultas/OAW04_consultation.wav --vision-fps 0.5 --output code/outputs/reproduction/full/anomaly --case-id caso_demo_sintetico` | Reúne as evidências de vídeo e áudio do exemplo com os dados sintéticos anômalos de sinais vitais e prescrições. As fontes pertencem a materiais diferentes; a associação é artificial. |
| 14 | `python code/scripts/replay_multimodal.py docs/resultados/reproduction_anomaly_case.json --speed 1 --output docs/resultados/replay_anomaly.jsonl` | Apresenta em sequência os eventos já calculados e salva o registro da reprodução a 1×. A latência medida aqui é de entrega dos eventos pré-calculados, não de inferência em tempo real. |

O script orquestrador copia os relatórios normal e integrado para `docs/resultados/`. Ele pode atualizar esses arquivos ao ser executado novamente. Métricas de tempo e memória podem variar conforme o computador, embora versões e entradas estejam registradas.

### 6.2 Reexecutar manualmente as etapas completas

Use esta alternativa somente se precisar depurar uma etapa ou entender o fluxo em partes. Execute os comandos na ordem da tabela anterior e use os mesmos argumentos. A reprodução completa automatizada é preferível para não esquecer uma etapa ou produzir relatórios de uma execução incompleta.

Se uma etapa falhar, corrija o problema e repita o comando que falhou. O download verifica arquivos incompletos e o manifesto permite conferir os recursos baixados. Não apresente métricas de execuções parciais como se fossem a avaliação completa.

## 7. Reexecutar uma etapa específica

Todos os comandos abaixo devem ser executados com o ambiente `.venv` ativado. O primeiro uso de Whisper, Qwen, YOLO ou OpenPose pode baixar pesos externos.

### Áudio e texto

```bash
python code/scripts/compare_whisper.py
```

Compara os modelos Whisper `tiny`, `base` e `small` nas consultas sintéticas OAW01/OAW04. Grava `docs/resultados/whisper_comparacao.json`.

```bash
python code/scripts/evaluate_vad.py
```

Compara WER no mesmo trecho sintético com e sem detecção de atividade de voz. Grava `docs/resultados/vad_comparacao.json`.

```bash
python code/scripts/evaluate_text.py
```

Executa a avaliação Qwen no conjunto fixo de 30 frases sintéticas. Grava `docs/resultados/text_evaluation.json`.

Para repetir apenas o ensaio de locutores, primeiro baixe as entradas sintéticas (se ainda não estiverem presentes), execute a análise e depois calcule as métricas:

```bash
python code/scripts/download_consultas_rehab26.py
python code/scripts/run_demo.py --audio data/public/consultas/OAW04_consultation.wav --normal --diarize --output code/outputs/diarizacao_experimental --case-id oaw04_diarizacao
python code/scripts/evaluate_diarization.py
```

O primeiro comando baixa OAW01/OAW04 e anotações. O segundo salva o relatório intermediário em `code/outputs/diarizacao_experimental/`. O terceiro atualiza `docs/resultados/diarizacao_sintetica.json`.

### Movimento

Para baixar as entradas e os modelos da avaliação visual:

```bash
python code/scripts/download_consultas_rehab26.py --video --participants all
python code/scripts/setup_vision_models.py
```

O primeiro comando obtém anotações, consultas sintéticas e vídeos dos cinco participantes. O segundo baixa os pesos OpenPose/YOLOv8 e verifica os checksums.

Para repetir a avaliação principal:

```bash
python code/scripts/evaluate_rehab26.py --sample-fps 0.5
```

O resultado é `docs/resultados/rehab26_lopo.json`. A execução pode ser longa. O arquivo reporta tanto as métricas como cobertura e casos inconclusivos; considere ambos ao interpretar o resultado.

Para recriar os clipes anotados de demonstração:

```bash
python code/scripts/prepare_rehab26_examples.py
python code/scripts/generate_vision_evidence.py --sample-fps 5
```

O primeiro comando prepara recortes curtos conforme os rótulos do REHAB26. O segundo executa os modelos nesses recortes e grava vídeos e resumos em `docs/resultados/vision_examples/`. Os resultados versionados indicam que os cinco clipes de erro não geraram eventos com as regras atuais.

### Dados sintéticos e integração

Para gerar separadamente o relatório normal:

```bash
python code/scripts/run_demo.py --normal --no-qwen --output code/outputs/demo/normal
```

Usa os CSVs normais sintéticos e desativa Qwen, que não é necessário nesse caso. O relatório detalhado fica em `code/outputs/demo/normal/relatorio.json`.

Para gerar separadamente um caso tabular anômalo:

```bash
python code/scripts/run_demo.py --no-qwen --output code/outputs/demo/anomaly
```

Usa os CSVs sintéticos anômalos e grava `code/outputs/demo/anomaly/relatorio.json`.

Para simular a chegada incremental dos registros tabulares anômalos a 1×:

```bash
python code/scripts/monitor_stream.py --speed 1 --output code/outputs/stream/eventos_anomalia.jsonl
```

Esse comando espera os tempos registrados nos CSVs e escreve eventos incrementais em JSONL. Ele não recebe sinais de sensores em tempo real e não processa áudio ou vídeo.

Para repetir a reprodução temporal de eventos multimodais já calculados:

```bash
python code/scripts/replay_multimodal.py docs/resultados/reproduction_anomaly_case.json --speed 1 --output docs/resultados/replay_anomaly.jsonl
```

Esse comando espera que a reprodução completa já tenha produzido `reproduction_anomaly_case.json`.

## 8. Reproduzir análises exploratórias do REHAB24-6

Os comandos desta seção recriam comparações exploratórias anteriores, separadas da avaliação principal do REHAB26. Eles são úteis para estudar a evolução da solução, mas não devem substituir os resultados finais do REHAB26 no relatório.

Primeiro, baixe o vídeo PM_001 e suas anotações e recorte os trechos corretos/incorretos:

```bash
python code/scripts/download_public_data.py
python code/scripts/prepare_video_samples.py
```

O primeiro comando baixa somente uma gravação REHAB24-6, metadados e um áudio de teste Whisper em inglês. O segundo recorta duas repetições de PM_001 de acordo com `Segmentation.csv`.

Rode a análise geométrica nesses dois recortes:

```bash
python code/scripts/evaluate_video.py
```

Gera uma comparação exploratória e vídeos anotados em `code/outputs/avaliacao/`.

Para reproduzir o teste adicional PM_101 e criar seis recortes de avaliação:

```bash
python code/scripts/evaluate_pm101.py
```

O script baixa o vídeo PM_101 se necessário, corta um segmento normal e cinco segmentos incorretos e registra `code/outputs/pm101/resultados.json`.

Os recortes PM_101 servem de entrada aos dois comandos seguintes:

```bash
python code/scripts/evaluate_repetition_demo.py
python code/scripts/evaluate_calibration.py
```

O primeiro compara as saídas por repetição; o segundo calibra limiares em dois trechos PM_001 e avalia os recortes PM_101. Ambos são ensaios pequenos e exploratórios, não uma estimativa clínica nem a avaliação principal do trabalho.

Para executar YOLOv8 e OpenPose em um quadro isolado do recorte incorreto:

```bash
python code/scripts/run_vision_models.py data/public/rehab_incorreto.mp4 --time 1 --output code/outputs/visao_modelos
```

Esse passo requer os arquivos gerados acima e os pesos instalados com `setup_vision_models.py`. O resultado pontual fica em `code/outputs/visao_modelos/resultado.json`.

## 9. Abrir a interface e simular a chegada de dados

### Interface Streamlit

Com o ambiente ativado:

```bash
streamlit run code/app.py
```

O Streamlit inicia um servidor local e normalmente abre o navegador. Se não abrir, use o endereço local apresentado no terminal. Na interface, selecione entradas disponíveis, execute a análise e confira eventos, estados de modalidade e evidências. Para encerrar o servidor, volte ao terminal e pressione `Ctrl+C`.

A interface processa as entradas selecionadas. Para a demonstração integrada previamente avaliada, abra os relatórios produzidos pela reprodução completa e compare-os com a saída da interface. As fontes de vídeo, áudio e dados sintéticos não são do mesmo paciente.

### Simulação tabular

A simulação `monitor_stream.py` (seção 7) apresenta registros de sinais vitais e prescrições conforme os tempos nos CSVs. Já `replay_multimodal.py` apresenta eventos multimodais previamente processados. Em ambos os casos, “1×” refere-se à sequência temporal demonstrativa; isso não torna a inferência de áudio/vídeo contínua nem mede o tempo completo de processamento como serviço online.

## 10. Processar as consultas públicas em português

Este passo é **separado** do comando `reproduce.py --full`. O código não baixa vídeos do YouTube. Os links, a autorização informada pela equipe e a proveniência estão em [FONTES.md](../contexto/FONTES_DADOS.md). Obtenha as mídias seguindo as condições aplicáveis da fonte e da plataforma. Use apenas cópias locais cujo processamento e exibição estejam autorizados.

Os arquivos locais devem ficar em `data/public/consultas/`, uma pasta ignorada pelo Git. Crie-a se necessário:

No macOS/Linux/Git Bash:

```bash
mkdir -p data/public/consultas
```

No PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path data/public/consultas | Out-Null
```

Se você já tem arquivos WAV autorizados, copie-os para essa pasta e use estes nomes:

- `data/public/consultas/terapia_manual.wav`
- `data/public/consultas/reabilitacao_quadril.wav`

macOS/Linux/Git Bash:

```bash
cp "/caminho/local/terapia_manual.wav" data/public/consultas/terapia_manual.wav
cp "/caminho/local/reabilitacao_quadril.wav" data/public/consultas/reabilitacao_quadril.wav
```

PowerShell:

```powershell
Copy-Item -LiteralPath "C:\caminho\local\terapia_manual.wav" -Destination "data/public/consultas/terapia_manual.wav"
Copy-Item -LiteralPath "C:\caminho\local\reabilitacao_quadril.wav" -Destination "data/public/consultas/reabilitacao_quadril.wav"
```

Se possui apenas vídeos autorizados localmente, extraia o áudio com FFmpeg, que foi disponibilizado no ambiente Python. Substitua os caminhos de entrada pelos nomes reais dos arquivos no seu computador.

macOS/Linux:

```bash
ffmpeg -i "/caminho/local/terapia_manual.mp4" -vn -ac 1 -ar 16000 -c:a pcm_s16le data/public/consultas/terapia_manual.wav
ffmpeg -i "/caminho/local/reabilitacao_quadril.mp4" -vn -ac 1 -ar 16000 -c:a pcm_s16le data/public/consultas/reabilitacao_quadril.wav
```

PowerShell:

```powershell
ffmpeg -i "C:\caminho\local\terapia_manual.mp4" -vn -ac 1 -ar 16000 -c:a pcm_s16le data/public/consultas/terapia_manual.wav
ffmpeg -i "C:\caminho\local\reabilitacao_quadril.mp4" -vn -ac 1 -ar 16000 -c:a pcm_s16le data/public/consultas/reabilitacao_quadril.wav
```

Depois, processe as duas entradas:

```bash
python code/scripts/process_public_consultations.py --therapy-audio data/public/consultas/terapia_manual.wav --hip-audio data/public/consultas/reabilitacao_quadril.wav
```

O processamento usa Whisper `small` e Qwen por padrão. Os relatórios integrais ficam em `code/outputs/consulta_real_terapia_completa/` e `code/outputs/consulta_real_quadril_completa/`; são locais e ignorados pelo Git. O resumo minimizado é escrito em `docs/resultados/consultas_publicas_resumo.json`, sem transcrição integral.

Para processar somente com Whisper e não executar a análise Qwen:

```bash
python code/scripts/process_public_consultations.py --therapy-audio data/public/consultas/terapia_manual.wav --hip-audio data/public/consultas/reabilitacao_quadril.wav --no-qwen
```

Não há transcrição humana revisada dessas gravações; portanto, esse processamento não calcula WER nem comprova a precisão da transcrição.

## 11. Conferir os resultados gerados

Abra estes arquivos no editor de texto ou execute o formatador JSON para lê-los no terminal:

```bash
python -m json.tool docs/resultados/reproduction_normal_case.json
python -m json.tool docs/resultados/reproduction_anomaly_case.json
python -m json.tool docs/resultados/whisper_comparacao.json
python -m json.tool docs/resultados/text_evaluation.json
python -m json.tool docs/resultados/rehab26_lopo.json
```

Cada linha formata um relatório diferente para leitura. O conjunto completo de resultados e o comando que os gera estão no [índice de resultados](../../../../Tech%20Challenge/Fase%204/docs/resultados/README.md). Os principais arquivos são:

| Evidência | Arquivo |
|---|---|
| Caso integrado com eventos e alertas | `docs/resultados/reproduction_anomaly_case.json` |
| Caso normal | `docs/resultados/reproduction_normal_case.json` |
| Eventos entregues na reprodução temporal | `docs/resultados/replay_anomaly.jsonl` |
| Comparação Whisper | `docs/resultados/whisper_comparacao.json` |
| Comparação VAD | `docs/resultados/vad_comparacao.json` |
| Avaliação textual Qwen | `docs/resultados/text_evaluation.json` |
| Avaliação visual REHAB26 | `docs/resultados/rehab26_lopo.json` |
| Índice de exemplos de visão | `docs/resultados/vision_examples/indice.json` |
| Hashes de vídeos/dados externos baixados | `docs/resultados/assets_externos_manifesto.json` |
| Hashes dos pesos YOLO/OpenPose | `docs/resultados/modelos_externos_manifesto.json` |

Ao interpretar números de áudio, texto e movimento, leia também as limitações e a cobertura. Os resultados são experimentais, baseados em conjuntos pequenos ou sintéticos em algumas modalidades, e não validam uso clínico.

## 12. Onde cada arquivo é armazenado

| Caminho | Conteúdo | Versionado no Git? |
|---|---|---|
| `code/src/fisio_fase4/` | Componentes de análise, regras, eventos e integração | Sim |
| `code/scripts/` | Instalação, download, avaliações e reprodução | Sim |
| `code/tests/` | Testes automatizados | Sim |
| `data/synthetic/` | Séries e frases sintéticas com rótulos fixos | Sim |
| `data/public/` | Mídias e pesos obtidos das fontes externas | Não; ignorado pelo Git |
| `code/outputs/` | Relatórios integrais locais e saídas intermediárias | Não; ignorado pelo Git |
| `docs/resultados/` | Métricas, manifestos e evidências selecionadas | Sim |

O download de materiais externos não os adiciona ao Git. Fontes, licenças e condições estão em [FONTES.md](../contexto/FONTES_DADOS.md). Materiais que já estão hospedados online são referenciados por links em vez de duplicados no repositório.

## 13. Solução de problemas

### O inicializador não encontra Python 3.12

Confira a versão com `python3.12 --version` no macOS/Linux ou `py -3.12 --version` no Windows. Instale Python 3.12 e execute o inicializador novamente com o nome correto do executável.

### Uma dependência foi instalada incorretamente

Com o ambiente ativado, tente primeiro reinstalar as versões fixadas no arquivo de dependências:

```bash
python -m pip install -r code/requirements.txt
python code/scripts/check_environment.py
```

Se a inconsistência persistir, recrie o ambiente:

macOS/Linux:

```bash
python3.12 code/scripts/setup_environment.py --reinstall
```

Windows:

```powershell
py -3.12 code/scripts/setup_environment.py --reinstall
```

`--reinstall` remove a pasta `.venv` existente e cria uma nova. Dados externos em `data/public/` e relatórios em `code/outputs/` não são removidos.

### FFmpeg não aparece no terminal

Ative `.venv` e execute:

```bash
python code/scripts/setup_ffmpeg.py
python code/scripts/check_environment.py
```

O primeiro comando disponibiliza o FFmpeg empacotado pela dependência `imageio-ffmpeg`; o segundo verifica novamente o ambiente.

### O download foi interrompido

Ative `.venv` e repita o comando que falhou. Os scripts reutilizam arquivos completos e removem arquivos temporários incompletos. Se o modelo OpenPose estiver corrompido, execute:

```bash
python code/scripts/setup_vision_models.py
```

### Pouco espaço ou sem necessidade de avaliar vídeo

Use `python code/scripts/reproduce.py --quick`. Não execute `--full`, pois ele baixa os vídeos externos necessários à validação visual.

### O resultado diferiu dos valores do relatório

Confira que executou Python 3.12, usou a versão do código correta e concluiu toda a reprodução. Os tempos podem mudar entre computadores. A avaliação visual depende dos vídeos e pesos externos; os checksums registrados nos manifestos ajudam a identificar os arquivos utilizados. Para a conclusão, use os números efetivamente escritos na execução e reporte divergências em vez de substituir métricas silenciosamente.

## Encerramento

Para uma primeira reprodução, siga as seções **3 a 6**, depois abra os relatórios da seção **11** e a interface da seção **9**. A seção **8** contém ensaios exploratórios anteriores; a seção **10** exige mídia autorizada obtida localmente e não faz parte do download automático. O roteiro e os resultados devem refletir o que a execução produziu, incluindo casos inconclusivos e erros observados.
