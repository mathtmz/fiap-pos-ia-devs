# Tech Challenge — Fase 4

Protótipo acadêmico de monitoramento multimodal em fisioterapia. Ele reúne análises experimentais de movimento, fala, sinais vitais e prescrições e apresenta eventos para revisão humana. **Não é uma ferramenta clínica.**

## Navegação

- [Índice dos relatórios, apresentação e guias](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/README.md)
- [Relatório final em PDF](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/relatorios/RELATORIO_FINAL_ENTREGA.pdf) · [Relatório em Markdown](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/relatorios/RELATORIO_FINAL_ENTREGA.md)
- [Roteiro de vídeo de 15 minutos](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/apresentacao/ROTEIRO_VIDEO.md)
- [Apresentação no Google Slides](https://docs.google.com/presentation/d/197YK_4hPVpuIkeAcYp2NySnGYusyQrff4fP8jsHPrpc/edit)
- [Manifesto de fontes, dados e modelos](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/contexto/FONTES_DADOS.md)
- [Resultados reproduzíveis](docs/resultados/)

## O que o projeto faz

1. Analisa movimentos de abdução do braço e produz eventos com evidências temporais.
2. Transcreve fala em português com Whisper e analisa trechos com Qwen 2.5.
3. Aplica regras didáticas a séries sintéticas de sinais vitais e prescrições.
4. Reúne eventos por caso e permite reproduzi-los em uma linha do tempo local.

O fluxo de reprodução a 1× demonstra a apresentação temporal dos alertas. Vídeo e áudio são analisados antes dessa reprodução; não existe monitoramento ao vivo nem integração hospitalar. As fontes de vídeo, áudio e dados sintéticos são distintas e sua associação em um caso é artificial.

## Pré-requisitos

- Python 3.12.
- Conexão com a internet para instalar dependências e obter dados ou pesos externos.
- Espaço em disco para dependências, modelos e vídeos públicos necessários à avaliação visual. Os arquivos são baixados sob demanda e não são versionados.

O ambiente testado usa dependências fixadas em [`code/requirements.txt`](code/requirements.txt). O projeto não exige credenciais ou chaves de API. O script de preparação verifica a versão do Python, cria o ambiente virtual, instala as dependências e configura FFmpeg.

## Início rápido

Na pasta `Tech Challenge/Fase 4`, execute o script com Python 3.12:

```bash
python3.12 code/scripts/setup_environment.py
```

No Windows, o inicializador usual é:

```powershell
py -3.12 code/scripts/setup_environment.py
```

Ative o ambiente criado:

```bash
source .venv/bin/activate
```

```powershell
.venv\Scripts\Activate.ps1
```

Obtenha as fontes públicas e os pesos necessários, respeitando as licenças listadas em [`FONTES_DADOS.md`](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/contexto/FONTES_DADOS.md):

```bash
python code/scripts/download_public_data.py
python code/scripts/download_consultas_rehab26.py
python code/scripts/download_consultas_rehab26.py --video --participants all --workers 3
python code/scripts/setup_vision_models.py
```

Execute os testes e abra a interface:

```bash
python -m pytest code/tests -q
streamlit run code/app.py
```

Na interface, **Demonstração preparada** já seleciona um vídeo de exercício e uma consulta simulada disponíveis em `data/public/`, junto dos dados sintéticos. Essa opção evita anexar arquivos manualmente; **Enviar arquivos próprios** permite trocar as mídias. Para estudar o fluxo e seguir os passos completos, consulte o [índice de materiais da entrega](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/README.md).

O Streamlit inicia em **Modo apresentação**, com a barra lateral recolhida e apenas os vídeos selecionados e os alertas com evidências em linguagem resumida. Expanda a barra para escolher as mídias ou os vídeos; mantenha-a recolhida durante a gravação. Desmarque o modo para consultar transcrições, métricas e detalhes JSON. Os vídeos anotados gerados na execução são convertidos para H.264 para reprodução no navegador.

### Preparar a gravação do vídeo

Com o ambiente ativado, este comando confere as dependências, gera os exemplos normal e anômalo, prepara o replay integrado e inicia a interface:

```bash
python code/scripts/prepare_recording.py --launch-app
```

Depois, siga o [roteiro cronometrado](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/apresentacao/ROTEIRO_VIDEO.md), que contém as falas, a ordem de telas e os comandos para a demonstração. Abra os [slides da apresentação](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/apresentacao/APRESENTACAO_FASE_4.pptx) antes de iniciar a gravação. Os arquivos gerados pelo preparo ficam em `code/outputs/recording/` e podem ser recriados com o mesmo comando.

## Experimentos e reprodução

Os resultados do relatório são reproduzidos pelos scripts de `code/scripts/`. A execução completa exige baixar os vídeos REHAB26 e os pesos dos modelos; os tamanhos e links estão no manifesto. Use o comando principal de reprodução para executar a sequência documentada:

```bash
python code/scripts/reproduce.py --quick
python code/scripts/reproduce.py --full --accept-external-downloads
```

`--quick` executa verificações que não exigem baixar mídia ou carregar modelos grandes. `--full` obtém as fontes externas necessárias e executa as avaliações completas; pode levar mais tempo e consumir alguns gigabytes de disco. A execução não baixa vídeos de consultas reais.

Para processar os dois vídeos públicos de consultas, obtenha os arquivos de áudio a partir dos links em [`FONTES_DADOS.md`](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/contexto/FONTES_DADOS.md) conforme a autorização da equipe e as condições da plataforma. Informe os caminhos locais ao script; os relatórios integrais ficam em `code/outputs/` (ignorado pelo Git) e somente o resumo sem transcrição é versionado:

```bash
python code/scripts/process_public_consultations.py \
  --therapy-audio /caminho/terapia_manual.wav \
  --hip-audio /caminho/reabilitacao_quadril.wav
```

Os dados de avaliação, parâmetros, separações por participante, métricas e exemplos anotados utilizados no relatório ficam em `data/synthetic/` e `docs/resultados/`. Saídas intermediárias e downloads ficam em `code/outputs/` e `data/public/`, ambos ignorados pelo Git. Mídias que já estão publicadas na internet são referenciadas por URL, não copiadas para o repositório.

## Modelos, autorização e licenças

- A instituição autorizou, conforme informado pela equipe, substituir Azure Speech/Text Analytics por Whisper e Qwen locais e dispensar o requisito geral de nuvem. O sistema não utiliza Azure nem requer acesso à nuvem.
- Whisper e Qwen baixam pesos na primeira utilização. O script `setup_vision_models.py` baixa e registra os hashes dos pesos YOLOv8n e OpenPose.
- Os pesos OpenPose são obtidos diretamente da fonte e verificados pelo checksum. Não são distribuídos no Git devido às restrições de licença. Consulte o manifesto antes de baixar ou reutilizar materiais.
- Mídias de atendimentos reais permanecem hospedadas nas fontes originais; o repositório contém links e resultados minimizados, sem transcrições integrais.

## Limitações conhecidas

- O protótipo não foi validado clinicamente e seus alertas não são diagnóstico ou recomendação de tratamento.
- O reconhecimento vocal de condições médicas não foi validado com áudios clínicos rotulados.
- A avaliação de movimento é exploratória e restrita ao exercício e aos rótulos descritos no relatório.
- A demonstração de tempo real é uma reprodução local; não existe integração com sensores ou equipe hospitalar.
- Latência e uso de memória dependem do sistema, versões instaladas e disponibilidade dos modelos externos.

## Solução de problemas

- **Versão Python incorreta:** execute o inicializador com Python 3.12 (`python3.12` ou `py -3.12`).
- **Erro `pyarrow requires NumPy 2.0 or newer`:** com o ambiente ativado, atualize as dependências fixadas com `python -m pip install -r code/requirements.txt` e execute `python code/scripts/check_environment.py`. O projeto fixa PyArrow numa versão compatível com NumPy 1.26.
- **FFmpeg ausente:** execute novamente `python code/scripts/setup_ffmpeg.py` dentro do ambiente virtual.
- **Download interrompido:** repita o comando correspondente; arquivos temporários incompletos são removidos pelo script.
- **Modelo ou fonte indisponível:** a origem e o comando estão em `Materiais/Fase 4 - AI Text & Media/Projeto de monitoramento multimodal/contexto/FONTES_DADOS.md`. A interface registra erro ou modalidade ausente sem descartar o relatório das demais entradas.
- **Pouco espaço em disco:** use `--quick` para verificar o ambiente sem baixar os vídeos e modelos da avaliação completa.

## Estrutura

```text
Fase 4/
├── code/
│   ├── app.py
│   ├── requirements.txt
│   ├── scripts/          # instalação, aquisição, avaliação e reprodução
│   ├── src/fisio_fase4/  # análises, eventos e orquestração
│   └── tests/
├── data/
│   ├── synthetic/        # entradas e rótulos produzidos para avaliação
└── docs/
    └── resultados/       # métricas e evidências finais versionadas
```

Relatórios, roteiros, apresentações e tutoriais ficam em [`Materiais/Fase 4 - AI Text & Media/Projeto de monitoramento multimodal/`](../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/README.md); esta pasta contém o projeto executável, os dados necessários e as evidências técnicas.
