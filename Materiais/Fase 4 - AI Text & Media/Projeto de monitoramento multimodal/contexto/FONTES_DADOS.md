# Fontes e dados

## Vídeo de exercício

ČERNEK, A. et al. *REHAB24-6: A multi-modal dataset of physical rehabilitation exercises*. Zenodo, 2024. DOI: [10.5281/zenodo.13305826](https://doi.org/10.5281/zenodo.13305826). Licença informada: CC BY-NC 4.0; os autores solicitam uso acadêmico ou de pesquisa sem fins comerciais e citação do trabalho relacionado. Consultar a [página da fonte](https://zenodo.org/records/13305826) antes de redistribuir.

O teste usa exercício 1 (abdução do braço), gravação `PM_001`, câmera 17. A tabela `Segmentation.csv` associa a repetição 1, quadros 130–324, a execução correta; a repetição 6, quadros 1690–1940, a execução incorreta. A gravação reúne voluntários em ambiente controlado, não pacientes internados; os rótulos de execução não identificam necessariamente a causa do erro. O script de preparação recorta e redimensiona os trechos. Os vídeos e os metadados são baixados para `data/public/`, excluídos do controle de versão.

## Áudio público

A amostra [jfk.flac](https://github.com/openai/whisper/blob/main/tests/jfk.flac) é distribuída no repositório de testes Whisper. É uma gravação de discurso em inglês e **não é consulta clínica**. A origem deve ser conferida antes de redistribuição; o projeto apenas fornece o script de download e a usa para uma verificação pontual de transcrição. Não há transcrição de referência revisada ou amostra pública clínica de fala neste repositório.

O [TAME Pain](https://physionet.org/content/tame-pain/1.0.0/) é um exemplo de recurso de fala rotulada relacionado a dor, mas possui acesso restrito; não foi baixado nem avaliado. Portanto, não se pode medir a detecção de fadiga, disartria ou falta de ar com os dados disponíveis.

## Dados sintéticos

`synthetic/vitais_*.csv` e `synthetic/prescricoes_*.csv` são exemplos artificiais criados exclusivamente para testar o código; não representam pacientes, medições clínicas ou prescrições válidas. Os tempos são segundos desde o início de um cenário demonstrativo. O identificador comum entre modalidades não prova que os registros sejam da mesma pessoa.

## Consultas sintéticas em português (OAW01 e OAW04)

BARBOSA, Ana. [FIAP Module 04 Fake Consultation](https://huggingface.co/datasets/ana-barbosa/fiap-module-04-fake-consultation), licença MIT declarada no cartão do conjunto. São conversas roteirizadas e sintetizadas por voz, não consultas reais, com transcrições de referência. Os roteiros tratam de pessoas fictícias em reabilitação com dor ou cansaço; os rótulos e a prosódia são simulados, portanto não servem como comprovação de detecção de alterações vocais clínicas.

OAW04 foi processado em português com três tamanhos do Whisper. A comparação reproduzível está em [`whisper_comparacao.json`](../../../../Tech%20Challenge/Fase%204/docs/resultados/whisper_comparacao.json) e mede WER agregado nas duas referências OAW01 e OAW04. Whisper `small` obteve 0/148 erros de palavra (WER 0%) em 14,434 s totais; `base`, 10/148 (WER 6,76%) em 6,395 s; `tiny`, 14/148 (WER 9,46%) em 4,275 s. A amostra contém somente duas consultas roteirizadas e sintetizadas, então a escolha de `small` como padrão é uma decisão experimental, não evidência de qualidade clínica. A avaliação Qwen em 30 frases artificiais está em [`text_evaluation.json`](../../../../Tech%20Challenge/Fase%204/docs/resultados/text_evaluation.json); F1 macro de sentimento 0,6067 e F1 de encaminhamento a alertas 0,9231. Os áudios OAW01 e OAW04 e seus roteiros são baixados para `data/public/consultas/` com `python code/scripts/download_consultas_rehab26.py`.

O arquivo [`text_evaluation_cases.json`](../../../../Tech%20Challenge/Fase%204/data/synthetic/text_evaluation_cases.json) contém 30 frases artificiais e rótulos fixos para medir sentimento, menção a termos e encaminhamento de negações e perguntas. As frases não são exemplos clínicos nem validam diagnósticos.

## Vídeos adicionais anotados de reabilitação (REHAB26-ViewAngles)

ČERNEK, A. et al. [REHAB26-ViewAngles](https://zenodo.org/records/23018128), licença CC BY-NC 4.0, pesquisa não comercial com atribuição. O conjunto apresenta gravações RGB de exercícios e anotações por repetição, vista e tipo de erro. O exercício 1 inclui amplitude insuficiente, braço flexionado, inclinação da cabeça, elevação do ombro e braço fora do plano. Os rótulos são de execução simulada sob condições controladas, não diagnósticos.

O exercício 1 possui 556 repetições anotadas em cinco participantes (Honza, Mima, Petra, Terka e Vasil), sendo 278 corretas e 278 incorretas. A avaliação separa participantes por validação cruzada leave-one-participant-out; cada pessoa é testada uma vez e os limiares são ajustados apenas nas outras quatro.

Os vídeos e as tabelas `Segmentation.csv`, `Segmentation.txt` e `Error_types.csv` são obtidos por link, com `python code/scripts/download_consultas_rehab26.py --video --participants all`. Os cinco vídeos somam aproximadamente 0,92 GiB. A aquisição usa até três conexões paralelas e informa progresso; os arquivos ficam localmente em `data/public/rehab26/`, ignorados pelo Git. Trechos curtos anotados produzidos pelo projeto e as métricas finais ficam em `docs/resultados/vision_examples/` e `docs/resultados/rehab26_lopo.json`; os arquivos originais não são duplicados no repositório. Na execução registrada, os cinco clipes de erro gerados não produziram eventos nas regras visuais atuais; essa falha está documentada no índice dos exemplos.

Os cinco tipos de erro são avaliados com medidas 2D: amplitude do braço, flexão do cotovelo, elevação relativa do ombro, inclinação da cabeça e uma aproximação lateral limitada para braço fora do plano. A medida lateral não recupera profundidade. YOLOv8 usa classes gerais para localizar a pessoa e objetos contextuais; não foi treinado para identificar regiões clínicas críticas.

### Teste adicional com PM_101 (REHAB24-6)

A gravação `Ex1/PM_101-Camera17-30fps.mp4` foi obtida e seis repetições foram testadas: uma anotada como correta (quadros 35–154) e cinco anotadas como incorretas (680–1296). A regra atual não emitiu alertas nas seis repetições: acertou o trecho correto e deixou de detectar os cinco incorretos. A fonte não especifica o tipo de erro em cada repetição dessa gravação. Os [resultados](../../../../Tech%20Challenge/Fase%204/docs/resultados/video_pm101.json) são reproduzidos por `python code/scripts/evaluate_pm101.py`; o teste demonstra que escolher outro vídeo, por si só, não melhora a regra.

## Candidatos de consultas reais pesquisados

A [Universidade de Warwick — Consultation Interaction](https://warwick.ac.uk/fac/soc/al/research/999respond/studenthub/consultation/) identifica quatro trechos da série britânica *GP: Behind Closed Doors* como consultas reais de atenção primária. São em inglês e podem servir como candidatos para análise de fala clínica:

- [Trecho 1](https://www.youtube.com/watch?v=sR1ZbQPQef4&t=298s)
- [Trecho 2](https://www.youtube.com/watch?v=W4PaUCBM4RQ)
- [Trecho 3](https://www.youtube.com/watch?v=pFfZtZITZmI)
- [Trecho 4](https://www.youtube.com/watch?v=26d2QbLpbMI)

A condição de consulta real é a identificação fornecida pela página da universidade. A disponibilidade, o conteúdo de cada vídeo e a autorização para baixar, converter, processar e exibir trechos no vídeo de entrega não foram confirmados. Eles não foram baixados nem processados; a indicação da universidade para assistir aos trechos não comprova licença para reutilizá-los no projeto.

Como candidato próximo ao domínio de fisioterapia, a [Clínica Universitaria La Salle — Terapia de espejo](https://www.clinicauniversitarialasalle.es/terapia-de-espejo/) apresenta a aplicação da terapia em paciente real. A página é em espanhol; ainda não foi confirmado se o trecho contém conversa suficiente para avaliação de transcrição ou se permite conversão e reutilização. Não foi incorporado ao projeto.

### Candidatos em português — pacientes reais

O canal do fisioterapeuta Robson Sitta descreve os dois vídeos abaixo como atendimentos de pacientes reais em sua clínica:

- [A terapia manual na prática! (ao vivo)](https://www.youtube.com/watch?v=Y3Au3GcBbbg), publicado em 04/11/2022 — atendimento de fisioterapia, segundo a descrição do autor.
- [Artroplastia de quadril: fisioterapia e recuperação no pós-operatório](https://www.youtube.com/watch?v=ihY3hJ9-RBg) — atendimento em reabilitação após cirurgia de quadril, segundo a descrição do autor.

Ambos são candidatos em português e alinhados ao contexto de fisioterapia. Os áudios foram transcritos localmente, sem referência humana revisada. O primeiro trecho contém fala de abertura e erros de transcrição; o segundo contém relato do profissional sobre reabilitação, mas não comprova diálogo entre profissional e paciente. A equipe informou que obteve autorização do autor para uso. Como os materiais originais permanecem hospedados no YouTube, este repositório registra os links acima e não replica os arquivos. Resultados reais são minimizados, sem transcrições integrais. A afirmação de que os pacientes são reais é do próprio autor e não foi confirmada independentemente.

## Pesos e modelos externos

- **OpenPose COCO:** arquitetura e pesos são obtidos com `python code/scripts/setup_vision_models.py`, verificados por checksum e mantidos localmente fora do Git. A licença oficial restringe a redistribuição e o acesso por terceiros; consulte a [licença OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/LICENSE).
- **YOLOv8n:** os pesos são obtidos pela Ultralytics na primeira execução; a versão do pacote é fixada em `code/requirements.txt`. Consulte a [documentação e licença Ultralytics](https://docs.ultralytics.com/).
- **Whisper e Qwen 2.5:** os pesos são baixados pelos pacotes oficiais na primeira utilização; os identificadores dos modelos são registrados nos resultados.

## Inventário de armazenamento

| Material | Fonte/consulta | Tratamento no Git |
|---|---|---|
| Código, scripts, testes e dependências | Produzidos no projeto | Versionados em `code/` |
| Dados vitais, prescrições e frases sintéticas | Produzidos para demonstração e avaliação | Versionados em `data/synthetic/` |
| Mídias e datasets públicos | URLs e timestamps neste documento | Referenciados; não copiados |
| Pesos dos modelos | Fontes citadas acima | Referenciados e obtidos sob demanda |
| Métricas, logs e exemplos anotados curtos | Produzidos pelos experimentos | Versionados em `docs/resultados/` |
