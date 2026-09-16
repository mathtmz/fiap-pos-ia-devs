# Tech Challenge — Fase 3: IA Generativa

Protótipo acadêmico de apoio à organização de evidências sobre síndrome dos ovários policísticos (SOP/PCOS). A solução combina um Qwen 2.5 0.5B-Instruct ajustado por QLoRA, uma chain LangChain, fluxo LangGraph, consulta parametrizada ao SQLite, recuperação de fontes e auditoria sanitizada.

O enunciado oficial está em [Materiais/Fase 3 - Generative AI/Tech Challenge/8IADT - Fase 3 - Tech challenge.pdf](../../Materiais/Fase%203%20-%20Generative%20AI/Tech%20Challenge/8IADT%20-%20Fase%203%20-%20Tech%20challenge.pdf). O [relatório técnico](./docs/RELATORIO_TECNICO.md), o [inventário de fontes](./docs/FONTES_CLINICAS.md) e o [roteiro do vídeo](./docs/ROTEIRO_VIDEO.md) detalham decisões, resultados e limites.

## Funcionalidade

O aplicativo Streamlit encaminha a pergunta para um grafo LangGraph que valida a entrada, consulta os registros SQLite, recupera até três fontes identificadas e avalia suficiência de evidências. Quando disponível, o adaptador local Qwen gera uma resposta por meio de uma chain LangChain. Citações são verificadas contra as fontes recuperadas; sem citação rastreável, o grafo descarta o texto do modelo e utiliza a resposta determinística `grounded_fallback`, registrada no trace.

Pedidos sobre hipóteses diagnósticas, prescrição e dose são aceitos como rascunhos para revisão médica. No corpus atual, não há resumo local clinicamente validado para sustentar decisões individuais, portanto o fluxo apresenta essa limitação e se abstém da conclusão. A decisão clínica final cabe ao médico responsável, que deve avaliar e validar qualquer conteúdo antes de orientar pacientes.

O projeto inclui 12 registros de demonstração em SQLite, quatro notas internas de demonstração e cinco referências institucionais rastreáveis. O conjunto de treinamento contém 600 exemplos sintéticos em partições 420/90/90. As referências institucionais têm emissor, edição e URL; seus resumos locais não passaram por revisão clínica. O inventário está em [docs/FONTES_CLINICAS.md](./docs/FONTES_CLINICAS.md), com um manifesto legível por máquina em `data/raw/source_manifest.json`.

## Resultados observados

- QLoRA concluído no Google Colab em GPU Tesla T4, por duas épocas. Perdas registradas: treino 2,7671, validação 2,6078 e teste 2,4071. O adaptador está em `code/outputs/lora_adapter`.
- Avaliação de recuperação em 44 perguntas: Precision@3 0,326, Recall@3 0,943 e MRR 0,879. Os 20 casos adicionados sobre referências institucionais recuperaram o documento esperado no top 3.
- Comparação de geração: 90 perguntas em três condições (270 respostas). Foram detectadas citações válidas em 1/90 respostas-base, 0/90 LoRA sem RAG e 0/90 LoRA com RAG. Consulte os arquivos em `code/outputs/metrics/` e a análise no relatório técnico.
- Testes locais: 48 aprovados. A comparação e as pontuações de rubrica são avaliações de engenharia exploratórias; não demonstram benefício, qualidade ou segurança clínica.

## Execução local no Windows

Abra PowerShell na raiz do repositório:

```powershell
Set-Location "Tech Challenge/Fase 3/code"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-model.txt
python scripts/generate_synthetic_cases.py
python scripts/ingest_corpus.py
python scripts/generate_instruction_data.py
python -m pytest tests -q -p no:cacheprovider
python scripts/run_evaluation.py
python scripts/run_demo.py
python -m streamlit run app.py
```

Python 3.12 é recomendado. A instalação PyTorch mostrada acima é para CPU; selecione a variante apropriada no site oficial do PyTorch para usar uma GPU NVIDIA local. A primeira inferência pode baixar o modelo-base do Hugging Face se ele ainda não estiver em cache. Sem o adaptador, o aplicativo usa o caminho determinístico.

## Treinamento e avaliação

O treinamento já foi executado. Para reproduzi-lo, gere o pacote de dados e código na pasta `code`:

```powershell
python scripts/create_colab_bundle.py
```

Envie `%TEMP%\fase3_colab_training_bundle.zip` ao notebook `docs/treinamento_colab.ipynb` no Google Colab, selecione uma GPU e execute as células. O treino gera `training_summary.json` e o adaptador LoRA. Para comparar novamente as três condições, com o adaptador instalado, execute:

```powershell
python scripts/run_generation_evaluation.py --limit 90
```

Para repetir as métricas e a rubrica exploratória:

```powershell
python scripts/run_evaluation.py
python scripts/evaluate_ai_review.py
```

## Entrega

O material técnico está consolidado neste repositório. Falta gravar e conferir o vídeo demonstrativo com duração máxima de 15 minutos. O [roteiro](./docs/ROTEIRO_VIDEO.md) contém sequência, narração e checklist. A revisão manual complementar da comparação pode enriquecer a análise, mas não é requisito expresso no enunciado. O protótipo não foi validado para uso clínico.

Notícias da Matéria 3 e exemplos literários da Matéria 5 são referências didáticas separadas: não integram o corpus médico nem o treinamento deste projeto.
