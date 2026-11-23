"""Report required runtime components without downloading models or media."""

from __future__ import annotations

import importlib.metadata
from packaging.requirements import Requirement
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    if sys.version_info[:2] != (3, 12):
        print(f"Expected Python 3.12; found {sys.version.split()[0]}.", file=sys.stderr)
        return 1

    missing, mismatched = [], []
    print(f"Python: {sys.version.split()[0]}")
    requirements = PROJECT_ROOT / "code" / "requirements.txt"
    for raw_line in requirements.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        requirement = Requirement(line)
        distribution = requirement.name
        try:
            version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            missing.append(distribution)
            continue
        print(f"{distribution}: {version}")
        if requirement.specifier and version not in requirement.specifier:
            mismatched.append(f"{distribution}=={version} (expected {requirement.specifier})")

    try:
        import imageio_ffmpeg

        print(f"FFmpeg: {imageio_ffmpeg.get_ffmpeg_exe()}")
    except Exception as exc:  # pragma: no cover - platform/runtime specific
        print(f"FFmpeg unavailable: {exc}", file=sys.stderr)
        missing.append("FFmpeg")

    if missing:
        print("Missing components: " + ", ".join(missing), file=sys.stderr)
        return 1
    if mismatched:
        print("Version mismatches: " + "; ".join(mismatched), file=sys.stderr)
        return 1
    print("Environment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
