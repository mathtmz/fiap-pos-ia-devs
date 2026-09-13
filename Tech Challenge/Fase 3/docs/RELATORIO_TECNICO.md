# Relatório técnico — Fase 3

## Objetivo e limites

Protótipo acadêmico para apoiar a organização de evidências sobre SOP/PCOS. Não é dispositivo médico, não fornece diagnóstico definitivo, prescrição, dosagem, tratamento individual ou interpretação clínica individual. Toda informação é sintética ou requer rastreabilidade explícita.

## Arquitetura

```text
Entrada validada (Pydantic)
  → bloqueio de PII / prompt injection / prescrição / diagnóstico
  → SQLite: somente registros sintéticos e query parametrizada
  → recuperação lexical do corpus rastreável
  → suficiência de evidência ou abstinência
  → resposta com fonte + validação de citação
  → log sanitizado
```

`build_langgraph()` materializa as etapas principais em LangGraph; `run_triage()` é o caminho determinístico usado nos testes e na demo offline. Os componentes de corpus, retrieval e prompt mantêm papéis equivalentes aos de LangChain, sem tornar a execução básica dependente de rede ou modelo remoto.

## Dados e fine-tuning

- `data/synthetic/pcos_synthetic.sqlite` é criado localmente com 12 registros explicitamente fictícios, sem nomes, contatos ou cópia de prontuários reais.
- `generate_instruction_data.py` produz 600 exemplos sintéticos: 420/90/90 para treino/validação/teste.
- LoRA: Qwen 2.5 0.5B-Instruct, 2 épocas, batch 1, acumulação 8; QLoRA é opcional para Colab GPU.
- Fine-tuning é reservado para formato, tom, recusa e limites. RAG é a fonte de fatos e protocolos mutáveis.
- O manifesto registra MedQuAD e PubMedQA como planejados e **não baixados**: a versão e licença devem ser verificadas antes de qualquer ingestão. O demo não apresenta conteúdo deles como se já estivesse disponível.

## Segurança e privacidade

O sistema recusa entradas com padrões de e-mail, telefone ou CPF; tentativas de prompt injection; e pedidos de prescrição, dose, diagnóstico ou tratamento individual. O modelo nunca escreve SQL: a camada interna usa placeholders. A auditoria registra somente UUID da execução, nó, decisão, fontes e latência; não registra pergunta nem identificação de paciente.

## Avaliação

Execute `python scripts/run_evaluation.py` após a ingestão. Métricas: Precision@3, Recall@3 e MRR. Para geração, a rubrica humana deve marcar fidelidade à fonte, completude, clareza, citações e segurança. A comparação a registrar é: modelo-base, LoRA sem RAG e LoRA + RAG; este repositório não inventa números de modelos que não foram treinados.

## Limitações reais

O corpus embarcado é propositalmente mínimo e fictício; a recuperação é lexical e não substitui embeddings/FAISS em uma avaliação robusta. O script de LoRA é uma configuração reproduzível, não prova de treinamento concluído. Resultados são demonstração de engenharia segura, não validação clínica nem evidência de eficácia.
