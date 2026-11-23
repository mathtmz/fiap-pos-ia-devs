"""Create the isolated Python environment and install the pinned dependencies."""

from __future__ import annotations

import argparse
import subprocess
import sys
import venv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_DIR = PROJECT_ROOT / ".venv"
REQUIREMENTS = PROJECT_ROOT / "code" / "requirements.txt"


def environment_python() -> Path:
    """Return the Python executable path for the current platform."""
    if sys.platform == "win32":
        return ENV_DIR / "Scripts" / "python.exe"
    return ENV_DIR / "bin" / "python"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare the Fase 4 virtual environment and dependencies."
    )
    parser.add_argument(
        "--reinstall",
        action="store_true",
        help="Recreate the project's .venv before installing dependencies.",
    )
    args = parser.parse_args()

    if sys.version_info[:2] != (3, 12):
        parser.error(
            f"Python 3.12 is required; current interpreter is {sys.version.split()[0]}. "
            "Run this script with Python 3.12."
        )

    if args.reinstall and ENV_DIR.exists():
        import shutil

        shutil.rmtree(ENV_DIR)

    if not environment_python().exists():
        print(f"Creating isolated environment: {ENV_DIR}")
        venv.EnvBuilder(with_pip=True, clear=False).create(ENV_DIR)

    python = environment_python()
    commands = [
        [str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(REQUIREMENTS)],
        [str(python), str(PROJECT_ROOT / "code" / "scripts" / "setup_ffmpeg.py")],
        [str(python), str(PROJECT_ROOT / "code" / "scripts" / "check_environment.py")],
    ]
    for command in commands:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)

    if sys.platform == "win32":
        activate = r".venv\Scripts\Activate.ps1"
    else:
        activate = "source .venv/bin/activate"
    print("\nEnvironment is ready.")
    print(f"Activate it with: {activate}")
    print("Then follow the Quickstart section in the Fase 4 README.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
