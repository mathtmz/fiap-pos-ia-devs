"""Create a small upload bundle containing only code and synthetic training data."""
import argparse
from pathlib import Path
from tempfile import gettempdir
from zipfile import ZIP_DEFLATED, ZipFile

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def bundle_files() -> list[Path]:
    files = [
        PROJECT_ROOT / "code" / "requirements.txt",
        PROJECT_ROOT / "code" / "requirements-model.txt",
        PROJECT_ROOT / "code" / "requirements-training.txt",
    ]
    for folder in (
        PROJECT_ROOT / "code" / "scripts",
        PROJECT_ROOT / "code" / "src",
    ):
        files.extend(
            path
            for path in folder.rglob("*.py")
            if "__pycache__" not in path.parts
            and path.name != "generate_synthetic_cases.py"
        )
    files.extend(
        (PROJECT_ROOT / "data" / "processed" / "instruction").glob("*.jsonl")
    )
    files.extend(
        (
            PROJECT_ROOT / "data" / "processed" / "corpus.jsonl",
            PROJECT_ROOT / "data" / "eval" / "retrieval_cases.jsonl",
        )
    )
    missing = [path for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Arquivos necessários ausentes: " + ", ".join(str(path) for path in missing)
        )
    return sorted(set(files))


def create_bundle(output: Path) -> Path:
    output = Path(output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for path in bundle_files():
            archive.write(path, path.relative_to(PROJECT_ROOT).as_posix())
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(gettempdir()) / "fase3_colab_training_bundle.zip",
    )
    args = parser.parse_args()
    archive = create_bundle(args.output)
    print(f"Pacote sintético para upload no Colab: {archive}")
    print("Nenhum prontuário real, chave ou dataset de notícias é incluído.")


if __name__ == "__main__":
    main()
