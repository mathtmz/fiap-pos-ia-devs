"""Builds a small, explicitly fictional local corpus for the offline academic demo."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed" / "corpus.jsonl"
MANIFEST = ROOT / "data" / "raw" / "source_manifest.json"

DOCUMENTS = [
    {"source_id": "SYN-PROTO-001", "title": "Protocolo fictício de triagem SOP", "version": "2026.1-ficticio", "text": "DOCUMENTO FICTÍCIO PARA FINS ACADÊMICOS. A triagem de síndrome dos ovários policísticos deve reunir história, sintomas, avaliação profissional e exclusão de outras causas. Não confirma diagnóstico."},
    {"source_id": "SYN-PROTO-002", "title": "Checklist fictício de pendências", "version": "2026.1-ficticio", "text": "DOCUMENTO FICTÍCIO PARA FINS ACADÊMICOS. Exames pendentes são alertas simulados e devem ser revisados por profissional habilitado; o assistente não solicita nem interpreta exames individualmente."},
    {"source_id": "SYN-FAQ-001", "title": "FAQ fictícia: limites do assistente", "version": "2026.1-ficticio", "text": "DOCUMENTO FICTÍCIO PARA FINS ACADÊMICOS. O assistente explica evidências disponíveis, cita fontes e explicita incerteza. Ele não prescreve medicamentos, doses, tratamentos ou diagnósticos definitivos."},
    {"source_id": "SYN-REPORT-001", "title": "Modelo fictício de laudo", "version": "2026.1-ficticio", "text": "DOCUMENTO FICTÍCIO PARA FINS ACADÊMICOS. Um resumo de triagem deve separar dados disponíveis, pendências simuladas, fontes consultadas, limitações e necessidade de validação humana."},
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(json.dumps(document, ensure_ascii=False) for document in DOCUMENTS) + "\n", encoding="utf-8")
    manifest = {
        "generated_at": "2026-09-13",
        "policy": "O demo usa somente documentos sintéticos. MedQuAD e PubMedQA não são redistribuídos nem baixados automaticamente.",
        "external_sources_planned": [
            {"name": "MedQuAD", "version": "a fixar antes do download", "license": "verificar na origem", "status": "not_downloaded"},
            {"name": "PubMedQA", "version": "a fixar antes do download", "license": "verificar na origem", "status": "not_downloaded"},
        ],
        "local_sources": [{key: doc[key] for key in ("source_id", "title", "version")} for doc in DOCUMENTS],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Corpus criado: {OUT}")


if __name__ == "__main__":
    main()
