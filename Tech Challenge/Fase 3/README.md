# Tech Challenge — Fase 3: IA Generativa

Protótipo acadêmico de assistente de evidências para triagem de SOP/PCOS, para a terceira fase da pós-graduação **IA para Devs** da FIAP POSTECH.

> Segurança clínica: este projeto usa somente dados sintéticos no demo. Não diagnostica, prescreve, recomenda dose ou substitui avaliação profissional.

O material didático consolidado está em [CONTEXTO_FASE3_IA_GENERATIVA.md](./CONTEXTO_FASE3_IA_GENERATIVA.md). O documento separa fatos extraídos das aulas de decisões ainda pendentes do enunciado oficial.

## Estrutura inicial

```text
Fase 3/
├── README.md
├── CONTEXTO_FASE3_IA_GENERATIVA.md
├── data/                 # corpus e dados de avaliação autorizados
└── code/
    ├── src/              # pacote da aplicação
    ├── scripts/          # ingestão, indexação, avaliação e execução
    ├── tests/            # testes automatizados
    └── outputs/          # métricas, figuras e relatórios gerados
```

## Execução local

```bash
cd "Tech Challenge/Fase 3/code"
# No macOS/zsh, crie e ative um ambiente isolado uma única vez:
python -m venv .venv
source .venv/bin/activate
# Remove apenas a sobreposição de ambiente e usa o espelho autenticado configurado pelo computador:
env -u PIP_INDEX_URL python -m pip install -r requirements.txt
python scripts/ingest_corpus.py
python scripts/generate_instruction_data.py
python -m pytest -q
python scripts/run_evaluation.py
streamlit run app.py
```

O demo padrão não baixa fontes públicas, não requer chaves e não chama modelos externos. Para o treinamento opcional em GPU/Colab, instale `requirements-training.txt` depois das dependências principais e use `python scripts/train_lora.py --run` (ou `--run --qlora` em GPU compatível). O modelo-base será baixado pelo `transformers` somente nessa execução explícita.

Consulte o [relatório técnico](./docs/RELATORIO_TECNICO.md) e o [material de vídeo](./docs/ROTEIRO_VIDEO.md). A estrutura preserva a separação entre fontes, implementação, testes e artefatos usada na Fase 2.
