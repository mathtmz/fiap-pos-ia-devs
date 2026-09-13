import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def pytest_sessionstart(session):
    from scripts.ingest_corpus import main
    main()
