# Relatório técnico — protótipo multimodal para fisioterapia

## 1. Resumo

Este relatório descreve a arquitetura, o método de avaliação e os resultados do protótipo acadêmico desenvolvido para o Tech Challenge da Fase 4. O sistema combina análise temporal de movimento, transcrição e interpretação de fala, regras para dados tabulares e associação de eventos em alertas rastreáveis. São utilizados OpenCV, MediaPipe Pose, OpenPose COCO, YOLOv8n, Whisper, Qwen 2.5 e Streamlit.

A instituição autorizou a substituição de Azure Speech to Text e Azure Text Analytics por Whisper e Qwen locais, conforme informado pela equipe. Assim, a execução não depende de serviços Azure, credenciais ou chamadas externas de processamento. Os resultados são exploratórios, não são avaliação clínica e não devem orientar diagnóstico ou tratamento.

## 2. Requisitos e escopo

O enunciado da Fase 4 solicita análise de vídeo e áudio, detecção de anomalias em sinais vitais, prescrições e movimento, integração multimodal, alertas, relatório técnico e vídeo demonstrativo. O protótipo implementa a arquitetura e oferece evidências de execução; as fontes não constituem um registro sincronizado de paciente. Vídeos de exercício, áudios de consulta e CSVs sintéticos são vinculados por um identificador de demonstração exclusivamente para ilustrar a fusão.

O escopo visual é o exercício de abdução do braço em vídeos de voluntários. Os testes de áudio com referência utilizam fala sintética roteirizada em português. Dois vídeos públicos em português foram processados localmente como consultas, conforme autorização de uso informada pela equipe; suas transcrições completas ficam ignoradas pelo Git. Estatísticas sem transcrição estão em [`resultados/consultas_publicas_resumo.json`](../../../../Tech%20Challenge/Fase%204/docs/resultados/consultas_publicas_resumo.json). Os sinais vitais, prescrições e frases anotadas são artificiais.

## 3. Organização da implementação

- `code/src/fisio_fase4/audio_text.py`: transcrição, análise textual e encaminhamento para revisão.
- `code/src/fisio_fase4/video.py` e `vision_models.py`: baseline MediaPipe, inferência YOLO/OpenPose e medidas temporais.
- `code/src/fisio_fase4/analysis.py`: regras de sinais vitais, prescrições e construção de eventos.
- `code/src/fisio_fase4/pipeline.py`: composição das modalidades, relatório e alertas por caso.
- `code/app.py`: interface Streamlit para carregar dados e inspecionar resultados.
- `code/scripts/`: instalação, aquisição de fontes, avaliações reproduzíveis e demonstração.
- `data/synthetic/`: entradas artificiais versionadas e conjunto de frases com rótulos fixos.
- `docs/resultados/`: resultados agregados, métricas, logs e evidências autorais.

Arquivos de mídia pública e pesos externos ficam localmente em diretórios ignorados pelo Git e são adquiridos por comandos reproduzíveis. Mídias hospedadas em plataformas públicas são referenciadas por link. O inventário, licenças, proveniência e tratamento de armazenamento estão em [`FONTES_DADOS.md`](../contexto/FONTES_DADOS.md).

## 4. Método

### 4.1 Vídeo

OpenCV lê o vídeo e seleciona amostras temporais. Em cada amostra, YOLOv8n detecta caixas de objetos e a pessoa principal. A região da pessoa é expandida com margem e enviada ao OpenPose COCO executado via OpenCV DNN. Para cada um dos 18 mapas, o máximo de confiança é convertido em coordenadas do quadro original. O código deriva ângulos articulares e razões normalizadas; quadros com pontos ausentes não são tratados como medições válidas.

MediaPipe fornece um baseline independente. As anotações de REHAB26-ViewAngles delimitam as repetições e os códigos de erro para avaliação. MediaPipe, YOLOv8 e OpenPose usam a mesma frequência e só executam nas amostras dentro desses intervalos, evitando inferência em partes não avaliadas do vídeo. Os limiares por característica são ajustados nas quatro pessoas de desenvolvimento e testados na quinta, repetindo o processo cinco vezes (leave-one-participant-out). As características de YOLOv8/OpenPose são armazenadas em cache para que a reprodução não repita essa inferência quando entradas, intervalos e frequência de amostragem não mudam.

As cinco regras experimentais associam características a baixa amplitude, flexão do cotovelo, elevação do ombro, inclinação da cabeça e projeção lateral do braço. A projeção lateral é apenas uma aproximação 2D. Os dados anotam movimentos controlados, não falhas cirúrgicas nem pacientes hospitalizados. YOLOv8n não possui categorias específicas para áreas críticas clínicas; OpenPose COCO não executa, nesta implementação, associação multipessoa completa.

### 4.2 Áudio, transcrição e texto

Whisper transcreve localmente com idioma `pt`. Foram comparados `tiny`, `base` e `small` nas mesmas gravações OAW01 e OAW04 e nas referências textuais fornecidas pelo conjunto. O WER usa palavras normalizadas por casefold e tokenização Unicode, sem pontuação. Tempo e memória de pico são medidos por execução.

O VAD foi comparado ligado e desligado no mesmo áudio sintético. Como o resultado ligado removeu fala e piorou o WER, a configuração padrão permanece sem VAD. Qwen 2.5 recebe blocos de transcrição e produz campos estruturados para análise textual; regras locais verificam a literalidade do trecho, negadores e perguntas para orientar encaminhamento à revisão. O conjunto de avaliação possui 30 frases artificiais.

A separação experimental de locutores usa agrupamento acústico local. A relação entre o grupo e os papéis de profissional/paciente depende de revisão humana. A métrica registrada para OAW04 seleciona retrospectivamente o melhor dos dois mapeamentos possíveis dos grupos, razão pela qual não é uma estimativa imparcial de DER. O resultado serve apenas como prova técnica inicial.

Medidas de velocidade de fala, pausas e silêncio são descrições acústicas. Como não há áudios clínicos rotulados e adjudicados, não há avaliação de detecção de fadiga, disartria ou dificuldade respiratória. Áudios públicos sem transcrição de referência são processados, mas não recebem WER ou rótulo de qualidade.

### 4.3 Dados tabulares e regras

Os arquivos sintéticos incluem frequência cardíaca, pressão sistólica/diastólica e SpO₂, além de dose e unidade de prescrições. O módulo avalia valores e variações consecutivas segundo regras configuradas no código. Cenários normal e anômalo possuem resultados conhecidos, empregados para testar a consistência da geração de eventos. Esses limites são didáticos e não são apresentados como valores clínicos universais.

### 4.4 Fusão, relatório e reprodução

Todos os eventos guardam `case_id`, tempo, modalidade, tipo, evidência, regra ou modelo, fonte e estado de revisão. A associação por caso e janelas temporais reúne os achados em alertas. A interface Streamlit expõe os arquivos e resultados; os scripts também geram `relatorio.json` para inspeção independente.

Os dados de sinais e prescrições são reproduzidos segundo os tempos indicados. Áudio e vídeo são processados em lote e, depois, eventos são apresentados em sequência a 1×. A latência de reprodução não mede a duração da inferência nem comprova operação contínua. Não há conexão com monitor hospitalar, prontuário ou canal de notificação.

## 5. Resultados

### 5.1 Reconhecimento de fala

| Whisper | Erros / palavras de referência | WER agregado | Tempo total | Pico médio de memória |
|---|---:|---:|---:|---:|
| `tiny` | 14 / 148 | 9,46% | 4,275 s | 577,2 MiB |
| `base` | 10 / 148 | 6,76% | 6,395 s | 815,9 MiB |
| `small` | 0 / 148 | 0% | 14,434 s | 2.165,6 MiB |

O padrão é `small` devido ao menor erro observado nas duas gravações sintéticas. O resultado deve ser interpretado somente nessa amostra. No teste OAW04, sem VAD o WER foi 15,38% e com VAD foi 80,77%; o VAD é desligado. Dados completos: [`whisper_comparacao.json`](../../../../Tech%20Challenge/Fase%204/docs/resultados/whisper_comparacao.json) e [`vad_comparacao.json`](../../../../Tech%20Challenge/Fase%204/docs/resultados/vad_comparacao.json).

### 5.2 Texto

Em 30 exemplos sintéticos, Qwen atingiu acurácia de sentimento 0,6333 e F1 macro 0,6067. O roteamento de eventos para alertas atingiu F1 0,9231 e o roteamento para revisão humana, F1 0,9000. As métricas e predições individuais estão em [`text_evaluation.json`](../../../../Tech%20Challenge/Fase%204/docs/resultados/text_evaluation.json). O conjunto pequeno e artificial não estima desempenho em diálogo clínico.

### 5.3 Diarização experimental

Em OAW04, foram alinhadas 78 palavras e 78 receberam grupo; a acurácia após o melhor mapeamento de grupos foi 1,0. O mapeamento foi selecionado com a referência e a amostra contém uma única consulta sintética. O número não é DER e não deve ser comparado a benchmarks independentes. Dados: [`diarizacao_sintetica.json`](../../../../Tech%20Challenge/Fase%204/docs/resultados/diarizacao_sintetica.json).

### 5.4 Movimento e modelos visuais

A avaliação por participante contém 556 repetições, distribuídas em cinco dobras. Com amostragem de 0,5 fps foram analisados 926 quadros; 256 (27,65%) produziram pose suficiente. A decisão binária OpenPose/YOLO pôde ser avaliada em 60 repetições (10,79% de cobertura) e deixou 496 inconclusivas. Sobre os casos avaliáveis, obteve 39 VP, 20 FP, 0 FN e 1 VN: precisão 0,661, recall 1,000 e F1 micro 0,7959. A média de F1 nas cinco dobras foi 0,8108. O baseline MediaPipe avaliou 406 repetições (73,02%) e obteve 187 VP, 184 FP, 14 FN e 21 VN: precisão 0,504, recall 0,9303 e F1 micro 0,6538. A comparação mostra que a cobertura da solução OpenPose/YOLO é insuficiente para interpretar o F1 como desempenho geral.

O F1 macro médio das cinco classes de erro foi 0,1776; os F1 micro por classe variaram de 0,119 a 0,298 e a cobertura por característica de 17,45% a 34,53%. A latência de inferência por quadro amostrado teve mediana de aproximadamente 2,35 s e P95 entre 2,36 e 2,37 s. A baixa visibilidade dos pontos, a exigência de pelo menos duas amostras válidas por repetição e as projeções 2D explicam parte da inconclusividade; os falsos positivos por classe mostram que as regras também precisam ser revistas. Nos cinco clipes de demonstração com erros rotulados, o sistema não emitiu eventos; o clipe normal também não emitiu eventos. Todos os dados por participante, tipo de erro e repetição estão em [`rehab26_lopo.json`](../../../../Tech%20Challenge/Fase%204/docs/resultados/rehab26_lopo.json), e as saídas dos clipes em [`vision_examples/indice.json`](../../../../Tech%20Challenge/Fase%204/docs/resultados/vision_examples/indice.json).

Os resultados anteriores de REHAB24-6, PM_101 e testes pontuais são baselines exploratórios independentes, não devem ser agregados à validação REHAB26. Os exemplos visuais curtos em `resultados/vision_examples/` permitem relacionar quadro e evidência, quando disponíveis.

### 5.5 Regras e cenário integrado

O cenário normal sintético produziu zero eventos e zero alertas; o cenário anômalo tabular produziu cinco eventos conhecidos (três de sinais vitais e dois de prescrições) e dois alertas. Na execução multimodal integrada foram gerados oito eventos (um de vídeo, dois termos textuais, três sinais vitais e duas prescrições) e dois alertas em 22,569 s. O evento de movimento identifica `low_abduction.mp4`, quadro 21 e o baseline MediaPipe; cada evento tabular ou textual identifica seu arquivo de origem. A reprodução temporal entregou 8/8 eventos com latência mediana de 9,879 ms e P95 de 10,508 ms. Essa latência cobre a entrega local dos eventos pré-calculados, não a inferência das modalidades. Resultados são indexados em [`resultados/README.md`](../../../../Tech%20Challenge/Fase%204/docs/resultados/README.md).

## 6. Avaliação crítica e limitações

1. **Representatividade:** os vídeos mostram voluntários em tarefas controladas; as falas com referência são sintetizadas e roteirizadas.
2. **Qualidade do rótulo e da amostra:** há cinco participantes e um exercício. Métricas por pessoa são mais informativas que inferências gerais, mas não substituem validação externa.
3. **Cobertura:** apenas 60 das 556 repetições (10,79%) foram avaliáveis pela regra binária OpenPose/YOLO. Poucos pontos visíveis ou poucas amostras resultam em saída inconclusiva; essa cobertura baixa impede interpretar o F1 como desempenho abrangente.
4. **Projeção 2D:** não estima profundidade e reduz a confiabilidade de um erro definido pelo plano de movimento.
5. **Voz clínica:** não há dados suficientes e rotulados para medir condições clínicas. Métricas de silêncio/ritmo não são diagnósticos.
6. **Consultas públicas:** não há referência humana revisada para calcular WER; somente metadados de execução minimizados são versionados.
7. **Integração:** a ligação entre fontes independentes é artificial; não há sincronização real de paciente ou sessão.
8. **Tempo real:** a reprodução de eventos calculados não representa processamento de ponta a ponta em fluxo contínuo.
9. **Licença e privacidade:** vídeos e pesos são obtidos diretamente das fontes sob seus termos; arquivos pessoais, mídias externas e transcrições integrais não são versionados.

## 7. Reprodutibilidade

1. Instalar Python 3.12 conforme [`README.md`](../../../../Tech%20Challenge/Fase%204/README.md) e fixações em `code/requirements.txt`.
2. Executar `python code/scripts/setup_environment.py` e ativar `.venv`.
3. Executar `python code/scripts/reproduce.py --quick` para validar ambiente, testes e cenários sintéticos.
4. Para refazer as avaliações, usar `python code/scripts/reproduce.py --full --accept-external-downloads`; os downloads externos e pesos ficam fora do Git.
5. Consultar versões, links, condições e hashes em [`FONTES_DADOS.md`](../contexto/FONTES_DADOS.md) e `docs/resultados/modelos_externos_manifesto.json`.

A avaliação completa pode demandar tempo e espaço para dependências, pesos e vídeos. O comando rápido não baixa esses itens. Os resultados versionados facilitam a consulta sem exigir a execução do fluxo completo.

## 8. Atendimento às entregas acadêmicas

| Entrega | Evidência | Situação |
|---|---|---|
| Código da solução | `code/src/`, `code/app.py`, scripts e testes | Implementado e reproduzível conforme README. |
| Fluxo, modelos e métodos | Este relatório e [`GUIA_REPRODUCAO_E_ESTUDO.md`](../reproducao/GUIA_REPRODUCAO_E_ESTUDO.md) | Documentados com escopo e limitações. |
| Resultados e exemplos de anomalia | `docs/resultados/` | Versionados; cenários de vitais e prescrições são sintéticos. |
| Serviços Azure solicitados no enunciado | Whisper e Qwen locais | Substituição autorizada pela instituição, conforme informado pela equipe. |
| Demonstração de até 15 minutos, publicada | [`ROTEIRO_VIDEO.md`](../apresentacao/ROTEIRO_VIDEO.md) | Pendente de gravação, publicação e inclusão do link pela equipe. |

## Referências

- OpenPose: <https://github.com/CMU-Perceptual-Computing-Lab/openpose>.
- Ultralytics YOLOv8: <https://docs.ultralytics.com/models/yolov8/>.
- OpenAI Whisper: <https://github.com/openai/whisper>.
- Qwen2.5-0.5B-Instruct: <https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct>.
- REHAB24-6: <https://doi.org/10.5281/zenodo.13305826>.
- REHAB26-ViewAngles: <https://zenodo.org/records/23018128>.
- FIAP Module 04 Fake Consultation: <https://huggingface.co/datasets/ana-barbosa/fiap-module-04-fake-consultation>.
- Enunciado da Fase 4: [`TECH_CHALLENGE_FASE_4.md`](../contexto/TECH_CHALLENGE_FASE_4.md).
