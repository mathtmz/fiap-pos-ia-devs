---
base_model: Qwen/Qwen2.5-0.5B-Instruct
library_name: peft
pipeline_tag: text-generation
tags:
- lora
- transformers
- triagem
---

# Adaptador LoRA para apoio à triagem

Adaptador PEFT treinado sobre `Qwen/Qwen2.5-0.5B-Instruct` para o assistente
acadêmico de apoio à triagem da Fase 3. O treinamento usa exemplos instrucionais
em português e o formato de resposta adotado pelo fluxo LangChain/LangGraph.

## Configuração

- **Método:** QLoRA, com quantização de 4 bits e treinamento somente dos módulos LoRA.
- **Base:** `Qwen/Qwen2.5-0.5B-Instruct`.
- **Dados:** conjunto instrucional local, particionado em treino, validação e teste.
- **Arquivos principais:** `adapter_model.safetensors`, `adapter_config.json` e os
  arquivos de tokenizer presentes nesta pasta.
- **Checkpoints:** mantidos fora do repositório por serem artefatos intermediários.

## Uso no projeto

O adaptador é carregado pelo módulo de inferência em
`code/src/fase3/model_runtime.py`. A aplicação combina a geração com a recuperação
de evidências no corpus local e os registros parametrizados do SQLite.

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
model = PeftModel.from_pretrained(base, "code/outputs/lora_adapter")
tokenizer = AutoTokenizer.from_pretrained("code/outputs/lora_adapter")
```

## Limitações de uso

O adaptador é um artefato de demonstração acadêmica. Suas respostas dependem das
evidências recuperadas e devem ser revisadas por profissional habilitado antes de
qualquer decisão clínica. Ele não substitui avaliação, diagnóstico ou prescrição
médica.

## Validação registrada

A configuração e os resultados do treinamento estão em `training_summary.json`.
As métricas de recuperação e a comparação entre condições de geração estão em
`code/outputs/metrics/` e são descritas no relatório técnico da Fase 3.