import json

from pcos_fase3.retrieval import retrieve


def test_retrieval_uses_accent_normalized_keywords_and_title_weight(tmp_path):
    corpus_path = tmp_path / "corpus.jsonl"
    docs = [
        {
            "source_id": "SOURCE-A",
            "title": "Diretriz internacional para adolescentes",
            "keywords": ["adolescência", "AMH", "ultrassom"],
            "text": "A avaliação considera os critérios recomendados na diretriz.",
        },
        {
            "source_id": "SOURCE-B",
            "title": "Modelo de auditoria",
            "keywords": ["logs", "rastreabilidade"],
            "text": "O registro guarda os identificadores técnicos da execução.",
        },
    ]
    corpus_path.write_text(
        "\n".join(json.dumps(document, ensure_ascii=False) for document in docs),
        encoding="utf-8",
    )

    result = retrieve("Quais orientações para adolescencia?", k=2, path=corpus_path)

    assert result[0]["source_id"] == "SOURCE-A"
    assert result[0]["score"] > 0


def test_retrieval_returns_empty_for_query_without_indexable_terms(tmp_path):
    corpus_path = tmp_path / "corpus.jsonl"
    corpus_path.write_text(
        json.dumps({"source_id": "SOURCE-A", "title": "Documento", "text": "Conteúdo."}),
        encoding="utf-8",
    )

    assert retrieve("de e com", path=corpus_path) == []
