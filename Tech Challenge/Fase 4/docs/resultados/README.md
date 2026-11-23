# Índice de resultados

Os artefatos desta pasta documentam execuções do protótipo. Os resultados medem comportamento experimental sobre os dados citados e não validam diagnósticos nem limites clínicos.

## Reprodução atual

| Arquivo | Conteúdo | Como gerar |
|---|---|---|
| [whisper_comparacao.json](whisper_comparacao.json) | WER agregado, tempo e memória de Whisper tiny/base/small em OAW01 e OAW04. | **python code/scripts/compare_whisper.py** |
| [text_evaluation.json](text_evaluation.json) | Métricas do Qwen, por sentimento, termo e encaminhamento, sobre 30 frases sintéticas fixas. | **python code/scripts/evaluate_text.py** |
| [vad_comparacao.json](vad_comparacao.json) | WER do Whisper tiny na mesma consulta sintética, com e sem VAD. | **python code/scripts/evaluate_vad.py** |
| [diarizacao_sintetica.json](diarizacao_sintetica.json) | Comparação exploratória de agrupamento de locutores, alinhada ao roteiro OAW04. | Fluxo completo ou run_demo com --diarize seguido de evaluate_diarization. |
| [rehab26_lopo.json](rehab26_lopo.json) | Avaliação de pose por cinco dobras, uma pessoa retida por teste; inclui cobertura, erros e evidências por repetição. | **python code/scripts/evaluate_rehab26.py** |
| [modelos_externos_manifesto.json](modelos_externos_manifesto.json) | Versões, fontes e SHA-256 dos pesos locais OpenPose e YOLOv8. | **python code/scripts/setup_vision_models.py** |
| [assets_externos_manifesto.json](assets_externos_manifesto.json) | SHA-256 e licença informada de cada entrada externa baixada para os experimentos. | **python code/scripts/download_consultas_rehab26.py --video --participants all --workers 3** |
| [reproduction_quick_normal.json](reproduction_quick_normal.json) | Saída do cenário normal com dados sintéticos. | **python code/scripts/reproduce.py --quick** |
| [reproduction_quick_anomaly.json](reproduction_quick_anomaly.json) | Eventos e alertas do cenário sintético anômalo. | **python code/scripts/reproduce.py --quick** |
| [vision_examples/indice.json](vision_examples/indice.json) | Índice dos exemplos curtos e anotados de movimento. Os cinco clipes de erro rotulado produziram zero eventos na regra atual. | **python code/scripts/generate_vision_evidence.py** |
| [consultas_publicas_resumo.json](consultas_publicas_resumo.json) | Resumo minimizado de execuções em dois vídeos públicos; não inclui transcrição. | `python code/scripts/process_public_consultations.py --therapy-audio CAMINHO_AUDIO_1 --hip-audio CAMINHO_AUDIO_2` |

## Resultados de demonstração integrada

Os arquivos [reproduction_normal_case.json](reproduction_normal_case.json), [reproduction_anomaly_case.json](reproduction_anomaly_case.json) e [replay_anomaly.jsonl](replay_anomaly.jsonl) são criados pela reprodução completa. O primeiro contém o caso sem eventos; o segundo reúne oito eventos de modalidades sintéticas e fontes de demonstração em dois alertas, sem afirmar que pertencem a uma pessoa real; o terceiro registra a entrega dos oito eventos pré-calculados durante a reprodução local a 1× (mediana 9,879 ms, P95 10,508 ms).

## Ensaios e baselines anteriores

Os arquivos **calibracao_exploratoria.json**, **repeticoes_demo.json**, **video*.json**, **vad_preliminar.json**, **vad_pausas_agrupadas.json**, **whisper_OAW01.json**, **consulta_oaw04.json** e **texto*.json** registram etapas exploratórias anteriores. Eles permanecem disponíveis para comparar a evolução e não devem ser tratados como substitutos das avaliações reproduzíveis atuais.

## Privacidade e proveniência

Transcrições integrais e áudios locais dos atendimentos públicos não são guardados nesta pasta. Os links originais e as informações de uso estão em [FONTES_DADOS.md](../../../../Materiais/Fase%204%20-%20AI%20Text%20%26%20Media/Projeto%20de%20monitoramento%20multimodal/contexto/FONTES_DADOS.md). Os resultados de mídia pública são limitados a metadados e métricas agregadas. Pesos e vídeos de origem ficam em pastas locais ignoradas pelo Git; os manifestos permitem conferir sua procedência sem redistribuir os arquivos.
