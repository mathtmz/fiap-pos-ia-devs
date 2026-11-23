"""Download referenced synthetic consultations and selected REHAB26 clips."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time
from urllib.request import urlretrieve

from remotezip import RemoteZip


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONSULTATIONS_DIR = PROJECT_ROOT / "data" / "public" / "consultas"
REHAB_DIR = PROJECT_ROOT / "data" / "public" / "rehab26"
RESULTS_DIR = PROJECT_ROOT / "docs" / "resultados"
CONSULTATIONS_URL = (
    "https://huggingface.co/datasets/ana-barbosa/fiap-module-04-fake-consultation/"
    "resolve/main/"
)
REHAB_URL = "https://zenodo.org/api/records/23018128/files/"
PARTICIPANTS = ("Honza", "Mima", "Petra", "Terka", "Vasil")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(url: str, target: Path) -> None:
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".part")
    try:
        urlretrieve(url, temporary)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def download_rehab_video(participant: str) -> Path:
    name = f"ex1_{participant}_cam1.mp4"
    target = REHAB_DIR / "videos" / name
    if target.exists():
        return target

    remote_name = f"videos/ex1/{name}"
    temporary = target.with_suffix(target.suffix + ".part")
    target.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, 4):
        try:
            with RemoteZip(
                REHAB_URL + "videos.zip/content", timeout=(15, 120)
            ) as archive:
                with archive.open(remote_name) as source, temporary.open("wb") as dest:
                    copied = 0
                    while chunk := source.read(1024 * 1024):
                        dest.write(chunk)
                        copied += len(chunk)
                        if copied and copied % (32 * 1024 * 1024) < len(chunk):
                            print(
                                f"{participant}: {copied / (1024**2):.0f} MiB downloaded",
                                flush=True,
                            )
            temporary.replace(target)
            return target
        except Exception:
            if attempt == 3:
                raise
            print(
                f"Retrying {participant} download ({attempt}/3)...",
                flush=True,
            )
            time.sleep(attempt * 2)
        finally:
            temporary.unlink(missing_ok=True)
    raise RuntimeError(f"Could not download video for {participant}.")


def write_local_asset_manifest(paths: list[Path]) -> Path:
    sources = {
        "FIAP Module 04 Fake Consultation": {
            "url": "https://huggingface.co/datasets/ana-barbosa/fiap-module-04-fake-consultation",
            "license": "MIT, conforme cartão do conjunto",
        },
        "REHAB26-ViewAngles": {
            "url": "https://zenodo.org/records/23018128",
            "license": "CC BY-NC 4.0, conferir os termos atuais da fonte",
        },
    }
    entries = []
    for path in paths:
        source = (
            "REHAB26-ViewAngles"
            if "rehab26" in path.parts
            else "FIAP Module 04 Fake Consultation"
        )
        entries.append(
            {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "source": source,
                "source_url": sources[source]["url"],
                "license": sources[source]["license"],
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    target = RESULTS_DIR / "assets_externos_manifesto.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "description": "Checksums of external assets downloaded for the experiments.",
                "entries": entries,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--video",
        action="store_true",
        help="Download exercise 1 videos for participant-wise evaluation (~1 GB total).",
    )
    parser.add_argument(
        "--participants",
        nargs="+",
        default=["all"],
        help="Participants to download: Honza Mima Petra Terka Vasil, or all (default).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=3,
        help="Number of concurrent video downloads (1–5; default: 3).",
    )
    args = parser.parse_args()

    CONSULTATIONS_DIR.mkdir(parents=True, exist_ok=True)
    REHAB_DIR.mkdir(parents=True, exist_ok=True)
    downloaded: list[Path] = []

    for name in (
        "OAW01_consultation.wav",
        "OAW01_transcript.json",
        "OAW04_consultation.wav",
        "OAW04_transcript.json",
    ):
        target = CONSULTATIONS_DIR / name
        download_file(CONSULTATIONS_URL + name, target)
        downloaded.append(target)

    for name in ("Segmentation.csv", "Segmentation.txt", "Error_types.csv"):
        target = REHAB_DIR / name
        download_file(REHAB_URL + name + "/content", target)
        downloaded.append(target)

    if args.video:
        if not 1 <= args.workers <= len(PARTICIPANTS):
            parser.error("--workers must be between 1 and 5.")
        requested = set(args.participants)
        if "all" in requested:
            requested = set(PARTICIPANTS)
        unknown = requested.difference(PARTICIPANTS)
        if unknown:
            parser.error("Unknown participant(s): " + ", ".join(sorted(unknown)))
        with RemoteZip(
            REHAB_URL + "videos.zip/content", timeout=(15, 120)
        ) as archive:
            index = {item.filename: item.file_size for item in archive.infolist()}
        total_bytes = sum(
            index.get(f"videos/ex1/ex1_{person}_cam1.mp4", 0)
            for person in requested
        )
        print(
            f"Downloading {len(requested)} external video(s), "
            f"approximately {total_bytes / (1024**3):.2f} GiB "
            f"using {min(args.workers, len(requested))} connection(s).",
            flush=True,
        )
        videos = []
        with ThreadPoolExecutor(max_workers=min(args.workers, len(requested))) as pool:
            futures = {
                pool.submit(download_rehab_video, person): person
                for person in PARTICIPANTS
                if person in requested
            }
            for future in as_completed(futures):
                path = future.result()
                videos.append(path)
                print(f"Completed {path.name} ({path.stat().st_size:,} bytes).", flush=True)
        completed = [
            REHAB_DIR / "videos" / f"ex1_{person}_cam1.mp4"
            for person in PARTICIPANTS
            if (REHAB_DIR / "videos" / f"ex1_{person}_cam1.mp4").is_file()
        ]
        downloaded.extend(sorted(set(videos + completed)))

    manifest = write_local_asset_manifest(downloaded)
    print(f"External assets are stored locally under {PROJECT_ROOT / 'data/public'}.")
    print(f"Local checksum manifest: {manifest}")
    print("These downloaded media files are excluded from Git by .gitignore.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
