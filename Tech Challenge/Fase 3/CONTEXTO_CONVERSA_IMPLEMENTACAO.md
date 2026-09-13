# Contexto da conversa de implementação — Fase 3

Data de consolidação: 2026-09-13.

## Objetivo acordado

Construir um assistente acadêmico de apoio à triagem de SOP/PCOS, em continuidade às Fases 1 e 2. O escopo é educacional: o sistema não emite diagnóstico definitivo, não prescreve, não recomenda dose e não substitui avaliação profissional.

## O que foi implementado

- Interface Streamlit para demonstrar pergunta educacional, paciente sintético, resposta, fontes e percurso do fluxo.
- Fluxo de triagem determinístico e representação opcional em LangGraph: validação, consulta de prontuário sintético, recuperação de evidência, avaliação de suficiência, resposta, revisão e auditoria sanitizada.
- SQLite local com 12 pacientes estritamente fictícios, exames simulados e pendências simuladas.
- Corpus local fictício com IDs, versões e trechos rastreáveis; manifesto declara MedQuAD e PubMedQA como fontes futuras ainda não baixadas.
- Geração reproduzível de 600 exemplos instrucionais sintéticos: 420 treino, 90 validação e 90 teste.
- Script de LoRA para Qwen 2.5 0.5B-Instruct, com duas épocas, batch 1, acumulação de gradiente 8 e QLoRA opcional para GPU/Colab.
- Avaliação de recuperação com Precision@3, Recall@3 e MRR; rubrica prevista para fidelidade, completude, clareza e citações.
- Relatório técnico, roteiro de vídeo e testes automatizados.

## Salvaguardas adotadas

- Validação de entrada com Pydantic.
- Recusa de padrões de PII, tentativas de prompt injection e pedidos de prescrição, dose, diagnóstico ou tratamento individual.
- A LLM não produz SQL; consultas ao SQLite usam placeholders parametrizados.
- Logs de auditoria excluem pergunta, identificador de paciente e dados clínicos; guardam somente execução, nó, decisão, fontes e latência.
- Conteúdo dinâmico da interface é exibido por componentes seguros do Streamlit, sem HTML inseguro.

## Verificação realizada

- `python -m pytest -q`: 10 testes aprovados.
- `python scripts/run_evaluation.py`: Precision@3 = 0,333; Recall@3 = 1,0; MRR = 0,5 no corpus sintético mínimo. Esses números não representam desempenho clínico.
- `python scripts/run_demo.py`: resposta contextualizada com fontes, pendência simulada e trace completo.

## Execução e dependências

O ambiente local usava um índice corporativo de pacotes que não forneceu Pydantic. A tentativa de PyPI público falhou por DNS/rede. A orientação atual é remover apenas a variável de ambiente que sobrescreve o espelho autenticado:

```bash
env -u PIP_INDEX_URL python -m pip install -r requirements.txt
```

Se o espelho autorizado continuar sem os pacotes, ele precisa ser ajustado pelo responsável pelo repositório de dependências. As dependências de demonstração ficam em `code/requirements.txt`; treinamento GPU/Colab fica em `code/requirements-training.txt`.

## Limitações declaradas

O corpus demonstrativo é intencionalmente pequeno e fictício; a recuperação é lexical; o treinamento LoRA não foi executado nesta máquina; não há validação clínica. Antes de uso além do contexto acadêmico, é necessário corpus autorizado, revisão de licença, avaliação clínica e controles operacionais adicionais.

## Privacidade do registro

Este arquivo resume decisões técnicas e erros de ambiente. Não inclui tokens, credenciais, dados pessoais nem prontuários reais.
