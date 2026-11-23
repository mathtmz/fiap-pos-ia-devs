# Roteiro de gravação — Tech Challenge Fase 4

**Duração planejada:** 15 minutos
**Formato:** apresentação com slides, demonstração breve da interface e inspeção de resultados no VS Code
**Arquivo de slides:** [`APRESENTACAO_FASE_4.pptx`](APRESENTACAO_FASE_4.pptx)

Este roteiro traz as falas em ordem, o que deve aparecer na tela e os comandos para preparar e gravar a demonstração. Depois de abrir o Streamlit, selecione o caso preparado e processe-o antes de iniciar a gravação; durante o vídeo, deixe a interface aberta no resultado. O exemplo combina um vídeo público de exercício, uma consulta sintética em português e dados tabulares sintéticos.

## 1. Preparação completa da gravação

Faça esta preparação antes de gravar: instale o ambiente, obtenha as mídias e os pesos que não estão no Git, aqueça os modelos e processe a demonstração no Streamlit. O script de gravação prepara os casos tabulares e abre a interface; o processamento multimodal deve ser executado nela antes da filmagem.

### 1.1. O que está no Git e o que precisa ser obtido

Os seis vídeos anotados em `docs/resultados/vision_examples/` **já estão versionados**. Há um exemplo normal e cinco exemplos rotulados (`arm_forward`, `shoulder_elevated`, `head_tilt`, `low_abduction` e `bent_arm`); consulte o [índice dos exemplos](../../../../Tech%20Challenge/Fase%204/docs/resultados/vision_examples/indice.json). Por exemplo, [`low_abduction/openpose_yolo_temporal.mp4`](../../../../Tech%20Challenge/Fase%204/docs/resultados/vision_examples/low_abduction/openpose_yolo_temporal.mp4) é uma saída pronta dos experimentos para abrir em um reprodutor. É um resultado anotado, não o vídeo bruto usado pela opção **Demonstração preparada**.

No modo **Demonstração preparada**, o Streamlit seleciona arquivos locais de `data/public/`; ele não baixa as mídias nem aceita um link do YouTube como entrada. Baixe os arquivos para a máquina antes da gravação. Para a demonstração integrada deste roteiro, serão usados:

| Entrada na interface | Arquivo local | Como obter | O que representa |
|---|---|---|---|
| Vídeo | `data/public/rehab_incorreto.mp4` | `download_public_data.py` e `prepare_video_samples.py` | Recorte curto público do REHAB24-6. |
| Áudio | `data/public/consultas/OAW04_consultation.wav` | `download_consultas_rehab26.py` | Consulta roteirizada e sintetizada em português; não é atendimento real. |
| Sinais vitais e prescrições | `data/synthetic/vitais_anomalia.csv` e `data/synthetic/prescricoes_anomalia.csv` | Já versionados; usados pelo seletor **Sinais e prescrição**. | Cenário artificial com anomalias conhecidas. |

Essas fontes não são registros da mesma pessoa. Na fala da apresentação, explique que a associação entre elas é artificial e serve para demonstrar a integração do protótipo. Os atendimentos em português hospedados no YouTube aparecem como referências em [`FONTES_DADOS.md`](../contexto/FONTES_DADOS.md); eles não são baixados automaticamente nem são necessários para reproduzir esta demonstração.

### 1.2. Ferramentas necessárias

| Ferramenta | Uso na gravação | Instalação/configuração |
|---|---|---|
| Git | Obter o repositório e seus arquivos versionados. | Instale o Git para seu sistema operacional, se ainda não estiver disponível. |
| Python 3.12 | Criar o ambiente e executar a aplicação. | [Downloads oficiais do Python](https://www.python.org/downloads/); instale uma versão Python 3.12 compatível com seu sistema. O projeto não funciona com outra versão. |
| VS Code | Mostrar código, relatórios e comandos. | [Baixar VS Code](https://code.visualstudio.com/download); abrir a pasta raiz do repositório. |
| Navegador atualizado | Abrir o Streamlit local e a apresentação Google Slides. | Chrome, Edge, Firefox ou Safari. Para evitar trocar de janela, use o mesmo navegador para Slides e o endereço local indicado pelo terminal (padrão `http://localhost:8501`). |
| Reprodutor de vídeo | Abrir o MP4 anotado versionado, se for mostrar a evidência separadamente. | QuickTime Player no macOS ou outro reprodutor compatível com MP4. |
| Gravador de tela e microfone | Registrar a tela e a narração. | No macOS, use Captura de Tela/QuickTime; em outros sistemas ou se precisar controlar cenas, use OBS Studio. |
| Internet e espaço livre | Instalar pacotes, baixar dados e pesos dos modelos. | Necessários durante a preparação inicial. O processamento e a interface rodam localmente; não são necessárias chaves de API. |

Caso precise obter uma cópia nova do repositório, instale o [Git](https://git-scm.com/downloads) e clone o projeto (é necessário ter acesso ao repositório):

```bash
git clone https://github.com/mathtmz/fiap-pos-ia-devs.git
cd fiap-pos-ia-devs
```

O instalador do projeto configura as bibliotecas Python e o FFmpeg usado pelos modelos. OpenPose, YOLOv8, Whisper e Qwen obtêm seus pesos na primeira preparação/execução e os mantêm localmente; esses arquivos não são adicionados ao Git. Reserve tempo para os downloads e para o primeiro processamento.

#### Gravar a tela no macOS

1. Conecte o microfone ou fone que será usado na narração e confirme que está selecionado nas configurações de som do sistema.
2. Pressione `Shift + Command + 5`.
3. Escolha **Gravar tela inteira** ou **Gravar porção selecionada**; a segunda opção evita mostrar notificações e outras janelas.
4. Abra **Opções**, escolha o microfone e uma pasta de destino com espaço livre, como `Filmes/TechChallengeFase4`.
5. Faça um teste de 20 segundos, pare a gravação e confira imagem e áudio antes de gravar o vídeo completo.
6. Para iniciar, abra novamente a barra, clique em **Gravar** e, para terminar, use o botão de parada na barra de menus.

Se o sistema pedir acesso ao microfone ou à gravação de tela, permita para o gravador escolhido e faça outro teste curto.

O guia oficial da [Apple para gravação da tela](https://support.apple.com/en-us/102618) descreve esses controles. Se preferir OBS, execute o assistente de configuração, crie uma cena, adicione captura de tela ou janela e o microfone, confira os medidores de áudio e faça uma gravação curta de teste antes da apresentação. Consulte o [guia oficial do OBS](https://obsproject.com/kb/quick-start-guide/).

Para abrir a apresentação, use **Apresentar** no Google Slides. Se optar pelo arquivo `.pptx`, abra-o no PowerPoint, Keynote ou LibreOffice e inicie a apresentação de slides. Deixe o gravador capturando a tela inteira ou apenas a área útil; confira que as janelas de navegador e VS Code não ficarão escondidas atrás da apresentação ao alternar entre elas.

### 1.3. Instalar o ambiente do projeto

Abra um terminal na raiz do repositório e entre na pasta da Fase 4:

```bash
cd "Tech Challenge/Fase 4"
```

No macOS/Linux, crie o ambiente virtual, instale as dependências fixadas e valide os pacotes:

```bash
python3.12 code/scripts/setup_environment.py
source .venv/bin/activate
python code/scripts/check_environment.py
```

No Windows PowerShell:

```powershell
py -3.12 code/scripts/setup_environment.py
.venv\Scripts\Activate.ps1
python code/scripts/check_environment.py
```

O inicializador cria `.venv`, instala os pacotes listados em `code/requirements.txt`, configura FFmpeg e executa uma verificação. Ative `.venv` sempre que abrir um terminal novo para trabalhar no projeto.

### 1.4. Baixar as entradas e preparar os modelos visuais

Com o ambiente ativo e o terminal ainda dentro de `Tech Challenge/Fase 4`, execute:

```bash
python code/scripts/download_public_data.py
python code/scripts/prepare_video_samples.py
python code/scripts/download_consultas_rehab26.py
python code/scripts/setup_vision_models.py
```

O primeiro script baixa o vídeo REHAB24-6 e as tabelas de segmentação; o segundo cria os recortes `data/public/rehab_correto.mp4` e `data/public/rehab_incorreto.mp4`; o terceiro baixa os áudios sintéticos OAW01/OAW04 e suas referências; o quarto obtém YOLOv8n e OpenPose, verifica os arquivos e grava um manifesto de checksums. Consulte as fontes e licenças em [`FONTES_DADOS.md`](../contexto/FONTES_DADOS.md). Os arquivos obtidos ficam em `data/public/`, pasta ignorada pelo Git.

Confirme que os dois arquivos selecionados pelo modo **Demonstração preparada** existem:

```bash
ls -lh data/public/rehab_incorreto.mp4 data/public/consultas/OAW04_consultation.wav
```

No Windows PowerShell, use:

```powershell
Get-Item data/public/rehab_incorreto.mp4, data/public/consultas/OAW04_consultation.wav
```

### 1.5. Aquecer os modelos e ensaiar o processamento

Whisper e Qwen baixam seus modelos na primeira utilização. Faça uma execução completa antes da gravação para baixar pesos, detectar problemas e confirmar que o fluxo funciona. Ela usa as duas entradas acima e as tabelas sintéticas anômalas:

```bash
python code/scripts/run_demo.py \
  --video data/public/rehab_incorreto.mp4 \
  --audio data/public/consultas/OAW04_consultation.wav \
  --vision-fps 0.5 \
  --output code/outputs/recording/multimodal_preflight \
  --case-id ensaio_multimodal
```

Este processamento é uma preparação; não use os arquivos de saída locais como se fossem dados clínicos ou como evidência de que vídeo e áudio vieram da mesma sessão. O relatório de ensaio fica em `code/outputs/recording/multimodal_preflight/relatorio.json`, pasta local ignorada pelo Git. Se a primeira execução demorar, aguarde até o terminal terminar e repita apenas se houver erro.

Depois gere os cenários normal/anômalo e abra o Streamlit:

```bash
python code/scripts/prepare_recording.py --launch-app
```

Esse comando verifica o ambiente, prepara cenários sintéticos e o replay integrado, e inicia o Streamlit. Ele não baixa mídia nem pesos. O terminal informa o endereço aberto (porta padrão `8501`); se o navegador não abrir automaticamente, digite esse endereço. Mantenha o terminal que está servindo a aplicação aberto.

### 1.6. Preparar a demonstração no Streamlit

Expanda a barra lateral da interface para conferir a seleção preparada. Depois de processar, recolha-a antes de começar a gravação:

1. Em **Identificador do caso**, escreva `demonstracao_fase4`.
2. Em **Origem das mídias**, mantenha **Demonstração preparada**. Isso usa os arquivos baixados para o projeto sem exigir upload manual.
3. Em **Vídeo do exercício**, escolha **REHAB24-6 · sequência com desvio**. Em **Áudio da consulta**, escolha **OAW04 · consulta simulada em português**.
4. Em **Sinais e prescrição**, selecione **Com alertas (sintéticos)**.
5. Abra **Configurações de análise** e mantenha Whisper **small**, VAD e agrupamento de locutores desligados, **Executar YOLOv8 e OpenPose ao longo do vídeo** e **Analisar transcrição com Qwen local** marcados. Use `3` quadros/s para o ensaio.
6. Clique em **Processar caso** e aguarde a conclusão. Se for a primeira execução, o Whisper ou Qwen pode baixar os pesos locais.
7. Deixe **Modo apresentação: mostrar vídeos e alertas** marcado. Em **Vídeos exibidos na apresentação**, mantenha selecionados **Mostrar vídeo de movimento** e **Mostrar vídeo com pontos corporais**.

Faça esta execução antes de começar a gravação e deixe a aba aberta no resultado. No modo apresentação, a tela principal mostra somente os vídeos selecionados e os alertas com suas evidências; transcrição JSON, métricas e detalhes técnicos ficam ocultos. A barra lateral já inicia recolhida; abra-a apenas para conferir ou trocar as opções. O resultado continua na sessão enquanto a aba não for atualizada ou fechada. Na execução atual, o processamento levou cerca de 86 segundos; processe o caso antes de gravar. Se quiser mostrar o processamento ao vivo, faça um ensaio cronometrado primeiro.

Se a interface avisar que uma mídia não ficou disponível, confira se executou os comandos de obtenção de dados e modelos da seção 1.5. Para usar outros arquivos, troque **Origem das mídias** para **Enviar arquivos próprios** e escolha cada arquivo nos campos exibidos.

#### Opcional: usar o áudio dos atendimentos em português do YouTube

Este roteiro principal usa OAW04 sintético para garantir uma entrada que qualquer pessoa consiga obter pelos scripts. Para demonstrar um dos áudios dos vídeos em português listados em `FONTES_DADOS.md`, é necessário ter a cópia local do vídeo e extrair o áudio; o endereço do YouTube não pode ser enviado ao Streamlit. Com o ambiente ativado, crie a pasta e converta cada arquivo local:

```bash
mkdir -p data/public/consultas
ffmpeg -i "/caminho/local/terapia_manual.mp4" -vn -ac 1 -ar 16000 -c:a pcm_s16le data/public/consultas/terapia_manual.wav
ffmpeg -i "/caminho/local/reabilitacao_quadril.mp4" -vn -ac 1 -ar 16000 -c:a pcm_s16le data/public/consultas/reabilitacao_quadril.wav
```

Substitua `/caminho/local/...` pelos caminhos reais dos arquivos. Na barra lateral, troque **Origem das mídias** para **Enviar arquivos próprios** e selecione um dos WAV gerados. Para essa demonstração, use apenas um áudio por vez e diga que ele vem de uma fonte diferente do vídeo e das tabelas sintéticas. As cópias locais permanecem fora do Git; o guia de [reprodução de consultas públicas](../reproducao/PASSO_A_PASSO_REPRODUCAO.md) descreve também a execução própria dessa análise.

### Deixe estas janelas abertas

1. **Apresentação:** abra [Google Slides](https://docs.google.com/presentation/d/197YK_4hPVpuIkeAcYp2NySnGYusyQrff4fP8jsHPrpc/edit) ou `Materiais/Fase 4 - AI Text & Media/Projeto de monitoramento multimodal/apresentacao/APRESENTACAO_FASE_4.pptx`; teste que a apresentação está acessível e pronta para iniciar.
2. **Streamlit:** mantenha a aba no endereço informado pelo terminal (padrão `http://localhost:8501`) com o resultado processado, sem atualizar a página.
3. **VS Code:** abra a raiz do repositório e deixe estes arquivos acessíveis pelo seletor rápido (`Ctrl+P` ou `Cmd+P`):
   - `Tech Challenge/Fase 4/code/src/fisio_fase4/pipeline.py`
   - `Tech Challenge/Fase 4/docs/resultados/reproduction_anomaly_case.json`
   - `Tech Challenge/Fase 4/docs/resultados/rehab26_lopo.json`
   - `Tech Challenge/Fase 4/docs/resultados/whisper_comparacao.json`
   - `Tech Challenge/Fase 4/README.md`
4. **Vídeo anotado versionado (opcional):** deixe à mão `Tech Challenge/Fase 4/docs/resultados/vision_examples/low_abduction/openpose_yolo_temporal.mp4`. Ele pode ser aberto no QuickTime ou em outro reprodutor; é uma saída de experimento separada e não é usada pela opção **Demonstração preparada**.
5. **Gravador:** deixe microfone correto selecionado, pasta de saída definida e resolução da tela testada. Feche notificações e aplicativos que possam cobrir a tela.

Antes de gravar, aumente a escala de texto do terminal, deixe o navegador largo o bastante para ler eventos e prepare a ordem de alternância entre slides, Streamlit, VS Code e reprodutor. A gravação começa na apresentação; a interface já estará processada em segundo plano.

## 2. Fala e sequência de tela

### 0:00–0:35 | Slide 1 — título

**Na tela:** capa da apresentação.

**Fala:**

> Olá. Neste vídeo vou apresentar o Tech Challenge da Fase 4, um protótipo acadêmico de monitoramento multimodal em fisioterapia. Vou explicar o fluxo, mostrar como os dados de vídeo, áudio e tabelas são tratados, apresentar os resultados medidos e terminar com uma demonstração reproduzível da interface e dos alertas.

### 0:35–1:25 | Slide 2 — objetivo e escopo

**Na tela:** slide “Objetivo do protótipo”.

**Fala:**

> O problema que investigamos é como organizar evidências que aparecem em modalidades diferentes: movimento em vídeo, relatos em áudio e texto, sinais vitais e prescrições. O objetivo foi implementar um fluxo que extraia eventos com instante, regra e fonte e os apresente para revisão humana. O protótipo não toma decisões clínicas. Para manter a avaliação delimitada, usamos abdução do braço na análise visual, consultas sintéticas em português para comparar transcrição e análise textual e séries sintéticas para testar as regras tabulares.

### 1:25–2:25 | Slide 3 — arquitetura

**Na tela:** diagrama com as três trilhas que convergem em eventos e alertas.

**Fala:**

> O fluxo tem três trilhas independentes. No vídeo, OpenCV seleciona os quadros, YOLOv8 localiza a pessoa e OpenPose estima pontos corporais; MediaPipe foi usado como comparação. No áudio, Whisper gera a transcrição e Qwen analisa os trechos de texto. Nas tabelas, regras explícitas verificam valores de sinais vitais e mudanças em prescrições. Cada processador pode produzir eventos com evidência e origem. O pipeline reúne esses eventos por caso e janela temporal. O relatório técnico preserva os detalhes em JSON; no modo apresentação do Streamlit, mostramos somente vídeos e alertas resumidos. Na demonstração, as fontes de modalidades diferentes são associadas para exercitar a integração, não para representar uma sessão única.

### 2:25–3:15 | Slide 4 — dados e avaliação

**Na tela:** tabela de fontes, quantidades e papel na avaliação.

**Fala:**

> A avaliação visual principal usa 556 repetições anotadas de cinco participantes do REHAB26-ViewAngles, com teste leave-one-participant-out. Como experimento adicional, usamos oito repetições de dois participantes do REHAB24-6. Para transcrição, comparamos Whisper em duas consultas roteirizadas e sintetizadas, com 148 palavras de referência. A análise textual usa 30 frases sintéticas rotuladas. Também processamos dois vídeos públicos em português e registramos medidas operacionais, como duração, segmentos, quantidade de palavras e tempo de processamento. Os CSVs de sinais vitais e prescrições foram construídos como cenários sintéticos normal e anômalo.

### 3:15–4:35 | Slide 5 — transcrição

**Na tela:** gráfico WER dos três tamanhos do Whisper e comparação de tempo.

**Fala:**

> Esta comparação usa as mesmas 148 palavras de referência. O Whisper tiny apresentou WER de 9,46 por cento e levou 4,275 segundos. O base teve WER de 6,76 por cento em 6,395 segundos. O small chegou a zero por cento nesta amostra, com 14,434 segundos de processamento e maior uso de memória. Por esse equilíbrio observado nas referências sintéticas, small foi escolhido como padrão da demonstração. Também avaliamos VAD. Em OAW04, o WER passou de 15,38 por cento sem VAD para 80,77 por cento com VAD. Isso mostra que a segmentação pode remover fala útil; por isso, a configuração da demonstração fica desligada.

### 4:35–5:25 | Slide 6 — análise textual

**Na tela:** métricas de sentimento, termos e revisão humana.

**Fala:**

> O Qwen 2.5 analisa trechos da transcrição, identifica termos candidatos como dor e cansaço e classifica o sentimento. As regras do projeto preservam a frase de origem e encaminham perguntas ou negações para revisão. Em 30 frases sintéticas, o F1 macro de sentimento foi 0,6067. O F1 para encaminhamento a alerta foi 0,9231, e para encaminhamento à revisão humana foi 0,9000. O agrupamento experimental de locutores usou MFCC e dois grupos acústicos. A identificação de papéis como profissional e paciente permanece revisável.

### 5:25–6:55 | Slide 7 — movimento

**Na tela:** gráfico de cobertura e F1 micro; em seguida, a quantidade de repetições inconclusivas.

**Fala:**

> No REHAB26, OpenPose combinado com YOLO avaliou 60 das 556 repetições, uma cobertura de 10,79 por cento. O F1 micro foi 0,7959 nos casos avaliáveis, enquanto 496 repetições ficaram inconclusivas. MediaPipe teve cobertura de 73,02 por cento e F1 micro de 0,6538. A classificação das cinco categorias específicas de erro teve F1 macro médio de 0,1776. Por isso, é essencial ler o F1 junto com a cobertura e com os resultados por classe. Os cinco clipes curtos de erro rotulado usados como exemplos também produziram zero eventos nas regras atuais. O sistema registra esses resultados com os quadros e as evidências correspondentes.

### 6:55–7:40 | Slide 8 — ensaio REHAB24-6

**Na tela:** treino em PM001, teste em PM101 e matriz de confusão 1/0/4/1.

**Fala:**

> Como ensaio adicional, calibramos uma regra de amplitude com duas repetições de PM001 e a aplicamos a seis repetições de PM101. O limiar foi 132,35 graus. O teste identificou uma repetição incorreta, não produziu falsos positivos e deixou quatro incorretas sem sinalização: recall de 0,20 e F1 de 0,333. Esse resultado mostra como o comportamento muda conforme a calibração e a variedade dos exemplos. O cálculo é exploratório e está registrado junto às previsões por repetição.

### 7:40–8:30 | Slide 9 — alertas integrados

**Na tela:** contagem dos cenários normal, anômalo e integrado; duração e latência de replay.

**Fala:**

> Nos CSVs tabulares, o cenário normal produziu zero eventos e zero alertas. O cenário anômalo gerou cinco eventos agrupados em dois alertas: três relacionados a sinais vitais e dois a alterações na prescrição. O caso integrado versionado reúne oito eventos em dois alertas e registra 22,569 segundos de processamento. A reprodução a um por um apresenta eventos já calculados; sua latência de entrega não mede a inferência de áudio ou vídeo. Na interface, cada evento mantém modalidade, instante, regra, evidência e arquivo de origem.

### 8:30–12:45 | Demonstração — terminal, Streamlit e VS Code

**Na tela:** use a segunda aba do terminal para os dois comandos; depois mostre os vídeos selecionados e os alertas no modo apresentação do Streamlit. Não faça downloads ou instalação durante a gravação.

**Ação e comando 1 — cenário normal:**

```bash
python code/scripts/run_demo.py --normal --no-qwen --output code/outputs/recording/normal --case-id caso_normal_gravacao
```

**Fala:**

> Primeiro executo o cenário normal com os CSVs sintéticos. A saída resume os estados das modalidades e mostra zero eventos e zero alertas. Isso dá uma referência para comparar com o cenário anômalo.

**Ação e comando 2 — cenário anômalo:**

```bash
python code/scripts/run_demo.py --no-qwen --output code/outputs/recording/anomaly --case-id caso_anomalo_gravacao
```

**Fala:**

> Agora executo o caso anômalo. O comando usa as séries sintéticas do projeto; não precisa baixar áudio, vídeo ou pesos de modelos. A saída mostra os eventos detectados e quantos alertas foram agrupados. Os valores principais são cinco eventos e dois alertas.

**Ação — interface:** volte ao navegador com **Modo apresentação: mostrar vídeos e alertas** ativado. Recolha a barra lateral para ocupar a tela com os resultados. Mostre os vídeos selecionados e os alertas; não abra transcrição ou JSON nessa parte. Se ainda não processou na interface, prepare e processe o caso antes de iniciar a gravação.

**Fala:**

> Na interface, vemos o vídeo do exercício com as marcações do movimento e dos pontos corporais. O primeiro grupo inclui um alerta experimental de amplitude, o relato de dor e os dados sintéticos de sinais e prescrição; o segundo reúne as evidências seguintes da demonstração. Essas entradas vêm de fontes diferentes e foram associadas artificialmente. Os alertas são candidatos para revisão humana, não diagnósticos.

**Ação — código no VS Code:** abra `code/src/fisio_fase4/pipeline.py` e destaque a criação e agregação dos eventos; depois abra `docs/resultados/reproduction_anomaly_case.json`.

**Fala:**

> No código, a função do pipeline recebe as modalidades disponíveis e reúne os eventos gerados. No relatório JSON é possível conferir o caso, as modalidades, as evidências, as regras, os instantes e os alertas. O arquivo versionado do caso integrado contém oito eventos e dois alertas; ele reúne resultados previamente calculados para demonstrar a estrutura multimodal.

**Ação — vídeo anotado:** se houver tempo, abra e reproduza `docs/resultados/vision_examples/low_abduction/openpose_yolo_temporal.mp4` no reprodutor de vídeo. Esse é um artefato versionado do experimento; ele é separado do vídeo processado na opção **Demonstração preparada** do Streamlit.

**Fala:**

> Este é um exemplo curto com os pontos e as detecções visuais anotados. A gravação permite conferir o quadro de origem e a pose que alimenta as medidas. Os números do gráfico continuam sendo a avaliação por participante do conjunto completo, não apenas o comportamento deste clipe.

**Ação e comando 3 — replay acelerado:**

```bash
python code/scripts/replay_multimodal.py docs/resultados/reproduction_anomaly_case.json --speed 12 --output code/outputs/recording/replay_during_video.jsonl
```

**Fala:**

> Por fim, reproduzo em velocidade acelerada a sequência temporal do relatório integrado. A aceleração serve para caber na demonstração; a ordem original dos eventos e suas evidências permanecem no arquivo JSONL gerado.

### 12:45–14:15 | Slide 10 — reprodução do projeto

**Na tela:** slide de reprodução; depois abra o README da Fase 4 no VS Code.

**Fala:**

> Depois de configurar o ambiente, baixar as mídias e ensaiar os modelos, a inicialização da demonstração pode ser repetida com um comando. O script verifica o ambiente, gera os dois cenários tabulares e prepara a reprodução integrada. O README da Fase 4 explica a instalação completa, os dados, os pesos e os experimentos. O passo a passo descreve onde cada saída é gravada. Os resultados usados neste vídeo estão no repositório, e as mídias públicas são referenciadas pelas fontes originais.

### 14:15–15:00 | Encerramento

**Na tela:** volte à capa ou permaneça no slide final.

**Fala:**

> Em síntese, implementamos e avaliamos um fluxo multimodal que transforma entradas distintas em eventos rastreáveis e alertas revisáveis. A demonstração mostrou o código, a interface, as evidências e a organização para reprodução. Os resultados deixam visíveis tanto as métricas quanto as condições em que foram obtidas. Obrigado.

## 3. Comandos de referência

### Preparar o ambiente e abrir a interface

```bash
python code/scripts/prepare_recording.py --launch-app
```

### Baixar o vídeo e o áudio de entrada e os pesos visuais

```bash
python code/scripts/download_public_data.py
python code/scripts/prepare_video_samples.py
python code/scripts/download_consultas_rehab26.py
python code/scripts/setup_vision_models.py
```

Após baixar, o modo **Demonstração preparada** seleciona por padrão `data/public/rehab_incorreto.mp4` e `data/public/consultas/OAW04_consultation.wav`; não é necessário anexá-los. Selecione **Enviar arquivos próprios** somente quando quiser processar outras mídias.

### Ensaiar a entrada multimodal e baixar os modelos de áudio

```bash
python code/scripts/run_demo.py \
  --video data/public/rehab_incorreto.mp4 \
  --audio data/public/consultas/OAW04_consultation.wav \
  --vision-fps 0.5 \
  --output code/outputs/recording/multimodal_preflight \
  --case-id ensaio_multimodal
```

O comando usa Qwen e Whisper localmente por padrão e gera um relatório de ensaio. Faça-o antes de abrir a interface para a gravação.

### Reproduzir apenas os casos tabulares durante a gravação

```bash
python code/scripts/run_demo.py --normal --no-qwen --output code/outputs/recording/normal --case-id caso_normal_gravacao
python code/scripts/run_demo.py --no-qwen --output code/outputs/recording/anomaly --case-id caso_anomalo_gravacao
```

### Reproduzir a sequência multimodal já calculada

```bash
python code/scripts/replay_multimodal.py docs/resultados/reproduction_anomaly_case.json --speed 12 --output code/outputs/recording/replay_during_video.jsonl
```

Os arquivos novos da gravação ficam em `code/outputs/recording/`, pasta ignorada pelo Git. Entradas baixadas ficam em `data/public/`, também ignorada pelo Git. O material usado como evidência permanece nos diretórios versionados `docs/resultados/`.

## 4. Solução de problemas antes de gravar

| Sintoma | Verificação e correção |
|---|---|
| A página avisa que vídeo/áudio está indisponível. | Mantenha **Demonstração preparada** e confira se os arquivos existem em `data/public/`. Para outras mídias, escolha **Enviar arquivos próprios** e use os campos de upload. |
| `data/public/rehab_incorreto.mp4` não existe. | Ative o ambiente e rode primeiro `download_public_data.py`, depois `prepare_video_samples.py`. |
| `OAW04_consultation.wav` não existe. | Rode `python code/scripts/download_consultas_rehab26.py` com internet ativa. |
| O processamento visual informa falta de pesos ou falha de modelo. | Rode `python code/scripts/setup_vision_models.py`, confira `python code/scripts/check_environment.py` e repita o ensaio. |
| Whisper ou Qwen falham ao baixar/carregar. | Confira conexão e espaço em disco; execute novamente o comando de ensaio antes da gravação. Não dependa do primeiro download durante o vídeo. |
| A tela mostra `pyarrow requires NumPy 2.0 or newer`. | Ative `.venv`, execute `python -m pip install -r code/requirements.txt` e depois `python code/scripts/check_environment.py`. O projeto fixa uma versão do PyArrow compatível com NumPy 1.26. |
| A interface não abre na porta `8501`. | Verifique o endereço informado pelo terminal. Se a porta estiver ocupada, use `python code/scripts/prepare_recording.py --launch-app --app-port 8502` e abra `http://localhost:8502`. |
| O resultado desaparece. | Não atualize nem feche a aba após processar. Se isso acontecer, selecione novamente **Demonstração preparada** e processe o caso outra vez antes de começar a gravação. |
| O microfone não aparece no arquivo final. | Confira a entrada selecionada no gravador e faça um novo teste de 20 segundos; a gravação de tela pode não incluir áudio do microfone por padrão. |

Para processar os vídeos reais em português do YouTube, use os links e as instruções da seção correspondente no [passo a passo de reprodução](../reproducao/PASSO_A_PASSO_REPRODUCAO.md). O Streamlit recebe um arquivo local de áudio, não um endereço do YouTube. Esses vídeos não são necessários para o fluxo principal de gravação deste roteiro.

## 5. Conferência de duração

- Faça um ensaio seguindo os tempos de cada bloco.
- A demonstração de tela começa em **8:30** e termina até **12:45**.
- Se passar do tempo, reduza o tempo de reprodução do vídeo anotado; preserve as falas com métricas e as explicações de cobertura visual.
- Termine com o slide de encerramento aos **15:00**.
