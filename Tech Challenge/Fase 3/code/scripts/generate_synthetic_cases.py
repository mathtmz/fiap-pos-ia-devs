"""Generate repeatable case profiles and an isolated demo-only diagnosis example."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "synthetic"

PROFILES = [
    {
        "patient_id": "SYN-PCOS-01",
        "age_band": "18-29",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Ciclos menstruais descritos como irregulares, com intervalos variáveis."},
            {"category": "Sinal relatado", "detail": "Acne recorrente informada na consulta."},
            {"category": "Histórico informado", "detail": "Relata que a irregularidade começou há cerca de um ano."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-02",
        "age_band": "18-29",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "A pessoa relata aumento de pelos faciais ao longo dos últimos meses."},
            {"category": "Ciclo informado", "detail": "Refere ciclos geralmente regulares."},
            {"category": "Histórico informado", "detail": "Não informou uso atual de medicamentos no registro."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-03",
        "age_band": "18-29",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Relata acne persistente, principalmente no rosto."},
            {"category": "Ciclo informado", "detail": "Refere variação na duração dos ciclos."},
            {"category": "Histórico informado", "detail": "Não há informação sobre início dos sintomas no registro."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-04",
        "age_band": "18-29",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Relata intervalos longos entre algumas menstruações."},
            {"category": "Sinal relatado", "detail": "Refere queda de cabelo percebida recentemente."},
            {"category": "Histórico informado", "detail": "Não informou histórico familiar no registro."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-05",
        "age_band": "18-29",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Refere ciclos irregulares desde a adolescência."},
            {"category": "Sinal relatado", "detail": "Informa acne ocasional."},
            {"category": "Histórico informado", "detail": "Relata que ainda não conversou com profissional sobre essas queixas."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-06",
        "age_band": "18-29",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Relata menstruações com duração variável."},
            {"category": "Sinal relatado", "detail": "Refere cansaço em alguns períodos do mês."},
            {"category": "Histórico informado", "detail": "Não há outros sintomas descritos neste registro."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-07",
        "age_band": "30-39",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Relata ciclos menstruais espaçados nos últimos meses."},
            {"category": "Sinal relatado", "detail": "Informa acne que reapareceu recentemente."},
            {"category": "Histórico informado", "detail": "Não informou mudança recente de rotina no registro."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-08",
        "age_band": "30-39",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Refere aumento de pelos no queixo."},
            {"category": "Ciclo informado", "detail": "Descreve ciclos com duração relativamente estável."},
            {"category": "Histórico informado", "detail": "Não há registro de avaliação anterior para esta queixa."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-09",
        "age_band": "30-39",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Relata irregularidade menstrual e desconforto antes da menstruação."},
            {"category": "Sinal relatado", "detail": "Refere pele mais oleosa que o habitual."},
            {"category": "Histórico informado", "detail": "Não informou duração exata das queixas."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-10",
        "age_band": "30-39",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Refere ciclos regulares e busca organizar informações de exames."},
            {"category": "Sinal relatado", "detail": "Não relata acne ou aumento de pelos neste registro."},
            {"category": "Histórico informado", "detail": "Não há resultados numéricos transcritos no registro."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-11",
        "age_band": "30-39",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Relata menstruações imprevisíveis."},
            {"category": "Sinal relatado", "detail": "Informa aumento de acne nos últimos meses."},
            {"category": "Histórico informado", "detail": "Não há informação sobre avaliação anterior no registro."},
        ],
    },
    {
        "patient_id": "SYN-PCOS-12",
        "age_band": "30-39",
        "reported_facts": [
            {"category": "Queixa relatada", "detail": "Refere mudança recente no padrão menstrual."},
            {"category": "Sinal relatado", "detail": "Não relata outros sintomas neste registro."},
            {"category": "Histórico informado", "detail": "O registro não contém resultados de exames numéricos."},
        ],
    },
]

DEMO_DIAGNOSIS = {
    "example_id": "DEMO-DX-001",
    "fictional": True,
    "demo_only": True,
    "not_for_triage": True,
    "title": "Exemplo didático de hipótese diagnóstica",
    "case_vignette": (
        "Vinheta separada dos registros: pessoa adulta relata ciclos irregulares e acne. "
        "Não há avaliação clínica nem resultados de exames apresentados neste exemplo."
    ),
    "mock_output": "Hipótese demonstrativa fictícia: síndrome dos ovários policísticos (SOP).",
    "disclaimer": (
        "O rótulo foi escrito manualmente apenas para demonstrar a apresentação de uma hipótese. "
        "Ele não foi inferido pelo assistente, não está associado a nenhum registro selecionado e "
        "não constitui avaliação clínica. Em uma situação real, o médico responsável deve avaliar "
        "e validar qualquer hipótese e mantém a decisão diagnóstica final."
    ),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    profiles_path = OUT / "case_profiles.jsonl"
    profiles_path.write_text(
        "\n".join(
            json.dumps({**row, "synthetic": True}, ensure_ascii=False)
            for row in PROFILES
        ) + "\n",
        encoding="utf-8",
    )
    (OUT / "demo_diagnosis.json").write_text(
        json.dumps(DEMO_DIAGNOSIS, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(PROFILES)} perfis sintéticos e exemplo isolado de demonstração gravados em {OUT}")


if __name__ == "__main__":
    main()
