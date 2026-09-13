# Roteiro do vídeo — TELA (o que executar/mostrar)

Tech Challenge Fase 2 — Projeto 1. Este arquivo contém apenas comandos, caminhos e o que
deve estar na tela em cada bloco. O texto a ser lido está em `ROTEIRO_VIDEO_FALA.md`, com as
mesmas seções e tempos.

---

## 0. Preparação (antes de iniciar a gravação)

Rodar tudo isso **fora** do vídeo, com o terminal já na pasta `Tech Challenge/Fase 2/code`:

```bash
source .venv/bin/activate
pip install -r requirements.txt

# Garantir estado limpo (sem execuções antigas de MLflow/logs)
rm -rf mlruns
rm -f outputs/logs/pipeline.log

# Gerar os artefatos que serão só exibidos durante a gravação (evita esperar processamento ao vivo)
python scripts/run_ga_experiments.py
python scripts/run_advanced_tuning.py
LLM_PROVIDER=mock python scripts/generate_llm_report.py
```

Checklist final antes de gravar:
- [ ] Terminal com fonte grande, sem chaves de API ou dados sensíveis visíveis.
- [ ] `outputs/figures/` com os gráficos já gerados (`fitness_evolution.png`, `advanced_tuning_fitness.png`, etc.).
- [ ] `outputs/reports/llm_explanation.md` já gerado.
- [ ] Editor aberto na raiz do projeto, pronto para alternar entre arquivos rapidamente.

---

## 1. Abertura (0:00 – 0:45)

**Mostrar:** `README.md` aberto no editor, com o título do projeto visível.

---

## 2. Estrutura do projeto e execução (0:45 – 2:00)

**Mostrar:** `README.md` e a árvore de pastas: `code/src/pcos_fase2`, `code/scripts`, `code/tests`.

**Executar no terminal:**
```bash
source .venv/bin/activate
python -m pytest tests -q
```

---

## 3. Baseline herdado da Fase 1 (2:00 – 3:00)

**Executar no terminal:**
```bash
python scripts/run_baseline.py
```

**Mostrar:** a tabela impressa no terminal com os 4 modelos baseline.

---

## 4. Algoritmo genético (3:00 – 6:30)

**Mostrar:** `code/src/pcos_fase2/genetic_optimizer.py`, destacando:
- `GENE_SPACES` (linha ~19)
- `tournament_selection` (linha ~134)
- `crossover` (linha ~107)
- `mutate` (linha ~119)

**Executar no terminal** (já deve estar pronto da preparação, só reexibir o resultado se quiser rodar ao vivo):
```bash
python scripts/run_ga_experiments.py
```

**Mostrar:**
- `code/outputs/figures/fitness_evolution.png`
- Tabela comparativa baseline vs. GA em `RELATORIO_TECNICO.md`, seção 4.

---

## 5. Escalabilidade automática e tracking (6:30 – 9:00)

**Mostrar:** terminal.

**Executar no terminal:**
```bash
python scripts/run_ga_experiment_grid.py --quick
```

**Destacar na tela:** a primeira linha de log impressa, do tipo:
```
... sera executada com N worker(s) (dimensionado automaticamente) ...
```

**Mostrar em seguida:**
```bash
cat outputs/logs/pipeline.log
```

**Opcional — abrir a UI do MLflow:**
```bash
mlflow ui --backend-store-uri ./mlruns
```
Abrir `http://127.0.0.1:5000` no navegador e mostrar o experimento `ga_jobs` com parâmetros,
métricas e o artifact `.jsonl`. Lembrar de encerrar o processo (`Ctrl+C` no terminal) depois
de mostrar.

---

## 6. Tuning avançado (9:00 – 9:45)

**Mostrar:** tabela de resultados de threshold em `RELATORIO_TECNICO.md`, seção 6.

---

## 7. Integração com LLM (9:45 – 13:00)

**Mostrar:** `code/src/pcos_fase2/llm_explainer.py`, destacando `SYSTEM_RULES` (linha ~13) e
`build_prompt` (linha ~27).

**Executar no terminal:**
```bash
LLM_PROVIDER=mock python scripts/generate_llm_report.py
cat outputs/reports/llm_explanation.md
```

**Mostrar no arquivo gerado:** as seções "Prompt usado", "Resposta gerada", "Checagem de
seguranca" e "Avaliacao de qualidade".

**Opcional, se tiver chave configurada:** repetir com
`LLM_PROVIDER=gemini GEMINI_API_KEY=... python scripts/generate_llm_report.py` e mostrar a
resposta real.

---

## 8. Testes e arquitetura (13:00 – 14:15)

**Executar no terminal:**
```bash
python -m pytest tests -v
```

**Mostrar:** a lista de arquivos em `code/tests/` passando rapidamente pela tela.

**Mostrar em seguida:** o diagrama Mermaid da seção "Arquitetura da solução" em
`RELATORIO_TECNICO.md` (renderizado no editor ou no GitHub).

---

## 9. Encerramento (14:15 – 15:00)

**Mostrar:** `README.md` e `RELATORIO_TECNICO.md` na tela, encerrando com os dois arquivos
visíveis.
