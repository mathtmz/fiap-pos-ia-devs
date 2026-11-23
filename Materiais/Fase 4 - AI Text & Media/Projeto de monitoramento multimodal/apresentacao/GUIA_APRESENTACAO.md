# Guia de estudo e apresentação

Este guia prepara a equipe para explicar as decisões, reproduzir os experimentos e responder às perguntas da banca. As métricas abaixo são experimentais e devem ser lidas junto ao [relatório final](../relatorios/RELATORIO_FINAL_ENTREGA.md) e aos arquivos de resultados.

## Problema, solução e dados

O projeto explora um fluxo que reúne sinais de quatro modalidades para apoiar a revisão de profissionais em um cenário acadêmico de fisioterapia. O fluxo recebe vídeos, áudios, séries de sinais vitais e prescrições, produz evidências temporais e agrupa alertas por caso. A equipe deve frisar que fontes diferentes foram associadas artificialmente; não representam uma única sessão ou paciente.

- **Movimento:** REHAB26-ViewAngles fornece repetições anotadas de cinco voluntários em exercício de abdução. Os rótulos descrevem execução controlada, não diagnóstico.
- **Áudio com referência:** OAW01 e OAW04 são consultas roteirizadas em português, sintetizadas por voz. Permitem calcular WER, mas não representam fala clínica espontânea.
- **Atendimentos em vídeos públicos:** os links e timestamps dos dois materiais em português estão em [Fontes](../contexto/FONTES_DADOS.md). A equipe informou ter autorização para uso. Os arquivos e as transcrições integrais não são versionados; sem referência humana revisada, não se calcula WER nem se valida a interpretação.
- **Sinais vitais e prescrições:** exemplos sintéticos definidos no projeto para produzir cenários normal e anômalo conhecidos.

## Fluxo técnico

1. **Vídeo:** OpenCV lê os quadros; YOLOv8 localiza pessoas e objetos de classes gerais; OpenPose COCO estima pontos 2D no recorte da pessoa principal. Medidas de amplitude do braço, cotovelo, elevação de ombro, inclinação da cabeça e projeção lateral são experimentais. MediaPipe permanece como baseline. Cada resultado preserva quadro, instante, modelo e confiança quando disponível.
2. **Áudio:** Whisper small, configurado para português, é o padrão após comparação de três tamanhos. O texto é analisado em blocos por Qwen 2.5; termos são vinculados a segmentos literais. Perguntas e negações são encaminhadas à revisão humana. Os papéis de locutor só são identificados pela equipe quando houver evidência.
3. **Anomalias:** regras configuráveis inspecionam os CSVs sintéticos de sinais vitais e alterações consecutivas de dose/unidade. Os limites são didáticos; não são faixas clínicas.
4. **Integração:** eventos preservam modalidade, evidência, fonte, tempo e regra. O agrupamento gera alertas em janelas temporais de 30 segundos.
5. **Demonstração:** a aplicação Streamlit processa arquivos carregados e exibe saída JSON. A reprodução a 1× agenda eventos já calculados; ela não é captura contínua nem integração hospitalar.

## Resultados que a equipe deve saber explicar

- Na comparação em duas consultas sintéticas (148 palavras de referência), small apresentou WER agregado de 0%, base de 6,76% e tiny de 9,46%. Os tempos totais observados foram, respectivamente, 14,434 s, 6,395 s e 4,275 s. Small foi escolhido como padrão por acurácia nessas amostras, mantendo os outros tamanhos disponíveis; isso não garante qualidade em consultas reais.
- Em OAW04, o VAD piorou o WER do Whisper tiny de 15,38% para 80,77%; permanece desligado por padrão. A medição está em [vad_comparacao.json](../../../../Tech%20Challenge/Fase%204/docs/resultados/vad_comparacao.json).
- Na única consulta sintética usada para avaliar diarização, 78 palavras foram alinhadas a grupos e a acurácia foi 100% após escolher retrospectivamente o melhor mapeamento entre os dois locutores. Isso não é DER e não representa desempenho em consultas reais; veja [diarizacao_sintetica.json](../../../../Tech%20Challenge/Fase%204/docs/resultados/diarizacao_sintetica.json).
- Em 30 frases sintéticas com rótulos fixos, Qwen obteve acurácia de sentimento 0,6333 e F1 macro 0,6067. O encaminhamento de eventos teve F1 0,9231; o encaminhamento para revisão de negações e perguntas teve F1 0,9000. A avaliação encontrou erros; os exemplos e a matriz por termo estão em [text_evaluation.json](../../../../Tech%20Challenge/Fase%204/docs/resultados/text_evaluation.json).
- No cenário normal sintético, a reprodução rápida gerou zero eventos e zero alertas. No cenário anômalo, foram cinco eventos (três vitais e duas prescrições) agrupados em dois alertas. Isso valida a execução das regras no cenário construído, não seu uso clínico.
- A avaliação visual por participante está em [rehab26_lopo.json](../../../../Tech%20Challenge/Fase%204/docs/resultados/rehab26_lopo.json). Em 556 repetições e 0,5 fps, OpenPose/YOLO avaliou 60 (10,79%); 496 foram inconclusivas. No conjunto avaliável, F1 micro foi 0,7959, com 20 falsos positivos; a cobertura baixa impede interpretar esse F1 como desempenho geral. MediaPipe avaliou 406 (73,02%) e teve F1 micro 0,6538. Os cinco clipes de exemplo com erro rotulado não geraram eventos. Explique a divisão leave-one-participant-out: quatro pessoas ajustam limiares e uma pessoa distinta é usada para teste em cada dobra. Mostre também as métricas por tipo de erro no JSON.
- A comparação dos modelos YOLO/OpenPose por quadro e suas limitações constam no manifesto de modelos e no resultado visual. Não descreva detecção de objetos gerais como identificação de área clínica crítica.
- Em dois áudios públicos descritos como atendimentos, o processamento integral gerou 151 palavras em 287,15 s e 5.075 palavras em 2.467,35 s. Sem referência manual, esses números descrevem o processamento e não medem qualidade da transcrição. Não inferir fadiga ou diagnóstico das medidas de pausa, silêncio ou ritmo.

## Perguntas prováveis

**Por que o projeto não usa Azure?** A instituição autorizou, conforme informado pela equipe, a substituição dos serviços em nuvem. O trabalho emprega Whisper para transcrição e Qwen 2.5 para análise textual localmente, sem chamadas Azure.

**O sistema identifica fadiga, disartria ou dificuldade respiratória?** Não. Silêncio, ritmo e outras medidas acústicas são descritores experimentais. Não há conjunto apropriado de fala clínica rotulada nem avaliação que sustente essa afirmação.

**O que significa WER de 0% para Whisper small?** Nestas duas gravações sintéticas e roteirizadas, a saída coincidiu com as referências após normalização de caixa e pontuação. O tamanho e a natureza da amostra não permitem extrapolar para fala espontânea.

**O que os números do Qwen demonstram?** Eles comparam saídas com rótulos fixos de 30 frases artificiais. Mostram acertos e erros do protótipo e permitem reproduzir a avaliação; não demonstram entendimento clínico.

**Como as anomalias foram validadas?** Os CSVs sintéticos têm valores e alterações conhecidos. Os testes verificam que as regras criam eventos e que os relatórios apontam para os dados de origem. Eles não equivalem a validação com pacientes.

**A solução funciona em tempo real?** Não como sistema de monitoramento contínuo. As modalidades são processadas em lote e os eventos finais são reproduzidos temporalmente a 1×. A latência medida é somente da entrega local dos eventos já calculados.

**O que falta para uso clínico?** Dados representativos com consentimento, rótulos e revisão especializada; validação independente e clínica; análise de segurança, privacidade e equidade; integração testada com fontes contínuas e processos hospitalares.

## Sequência sugerida para a demonstração

1. Apresente o problema, a autorização institucional para substituir Azure e as fontes de dados.
2. Mostre a avaliação visual por participante, incluindo um acerto, um erro e um caso inconclusivo; abra o quadro/trecho de evidência correspondente.
3. Compare a saída dos três Whisper no JSON e mostre uma transcrição sintética junto ao seu roteiro.
4. Abra exemplos de acerto e erro na avaliação textual do Qwen, incluindo negação/pergunta.
5. Execute o cenário normal e o cenário anômalo sintéticos; siga um evento até seu alerta e evidência.
6. Mostre a interface, a reprodução temporal a 1× e a matriz de requisitos do relatório.
7. Termine com as limitações e explique como reproduzir pelo [README](../../../../Tech%20Challenge/Fase%204/README.md).

Grave o vídeo dentro do limite de 15 minutos. Confira antes as condições de exibição das mídias, a privacidade dos dados, a duração e o áudio. Após publicar no YouTube ou Vimeo, adicione o link no [roteiro](ROTEIRO_VIDEO.md) e no relatório final.
