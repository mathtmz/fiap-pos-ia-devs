# Fontes institucionais do corpus

Conferência de metadados e links realizada em 15/09/2026. O corpus usa resumos curtos para busca e resposta; não redistribui cópias integrais das publicações.

| ID local | Fonte original e edição | Conteúdo representado no resumo local | Situação do resumo |
|---|---|---|---|
| `BR-MS-PCDT-SOP-2019` | [PCDT de SOP no Ministério da Saúde](https://www.gov.br/saude/pt-br/assuntos/pcdt/s/sindrome-de-ovarios-policisticos/view), Portaria Conjunta nº 6, 02/07/2019 | Critérios gerais descritos no PCDT e avaliação de causas alternativas. O portal do Ministério informa atualização da página em 21/01/2025; o PDF acessado continua identificado como protocolo aprovado em 2019. | Fonte oficial conferida; paráfrase local ainda não revisada clinicamente. |
| `INT-ASRM-PMOS-2023-ADULT` | [Recomendações internacionais de 2023, hospedadas pela ASRM](https://www.asrm.org/practice-guidance/practice-committee-documents/recommendations-from-the-2023-international-evidence-based-guideline-for-the-assessment-and-management-of-polyendocrine-metabolic-ovarian-syndrome-2023/) | Critérios gerais para adultas e papel do AMH como alternativa ao ultrassom em situações previstas na diretriz. | Fonte profissional conferida; paráfrase local ainda não revisada clinicamente. |
| `INT-ASRM-PMOS-2023-ADOLESCENT` | Mesma recomendação internacional de 2023 | Cautelas específicas para adolescência: considerar conjuntamente os achados indicados e não usar ultrassom ou AMH para estabelecer o diagnóstico nessa faixa etária. | Fonte profissional conferida; paráfrase local ainda não revisada clinicamente. |
| `INT-ASRM-PMOS-2023-EVIDENCE` | Mesma recomendação internacional de 2023 | A diretriz resume 254 recomendações/pontos de prática e registra qualidade geral da evidência baixa a moderada. | Fonte profissional conferida; paráfrase local ainda não revisada clinicamente. |
| `MONASH-PMOS-GUIDELINE-2026-PORTAL` | [Portal MCHRI/Monash da diretriz](https://www.monash.edu/medicine/mchri/pcos/guideline) e [PDF da diretriz de 12/06/2026](https://www.monash.edu/__data/assets/pdf_file/0009/4360095/Updated-PMOS-Guideline-12-June26.pdf) | Metadados para localizar a edição atual e a informação institucional de que PMOS é o novo nome anunciado em 12/05/2026 para a condição antes chamada PCOS. | O portal e os metadados foram conferidos. O PDF de 2026 não foi incorporado nem resumido clinicamente no corpus; use o portal/documento integral para confirmar recomendações atuais. |

## Como interpretar a validação

Cada resumo mantém `clinical_validated=false` e `supports_individual_decisions=false`. Isso distingue a autoridade da publicação original da revisão do texto local e impede que o retriever trate uma paráfrase como autorização automática para concluir diagnóstico, prescrever ou informar dose a uma pessoa. A equipe pode abrir o link original para conferência; qualquer uso individual exige avaliação e decisão do médico responsável.

Os quatro registros `SYN-*` são notas internas para demonstrar o fluxo e as regras do protótipo, não publicações médicas. O código registra também `publisher`, `published`, `checked_on`, `review_status`, `source_url`, palavras-chave de recuperação e um escopo de uso. A avaliação das 44 perguntas mede recuperação técnica dos IDs esperados, não validade médica do resumo.
