import json

from scripts import ingest_corpus


def test_ingest_creates_missing_manifest_directory(tmp_path, monkeypatch):
    corpus_path = tmp_path / "data" / "processed" / "corpus.jsonl"
    manifest_path = tmp_path / "data" / "raw" / "source_manifest.json"
    monkeypatch.setattr(ingest_corpus, "OUT", corpus_path)
    monkeypatch.setattr(ingest_corpus, "MANIFEST", manifest_path)

    ingest_corpus.main()

    assert corpus_path.is_file()
    assert manifest_path.is_file()
    corpus = [json.loads(line) for line in corpus_path.read_text(encoding="utf-8").splitlines()]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(corpus) == len(ingest_corpus.DOCUMENTS) == 9
    assert len(manifest["local_sources"]) == 9
    assert len(manifest["external_sources"]) == 5
    assert all(source["source_url"].startswith("https://") for source in corpus if source["source_url"])
    assert all(source["clinical_validated"] is False for source in corpus)
    assert all(source["supports_individual_decisions"] is False for source in corpus)
    assert "incorporado ao corpus" in manifest["source_review"].casefold()
