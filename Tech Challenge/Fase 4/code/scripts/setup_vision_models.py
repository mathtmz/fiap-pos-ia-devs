"""Download and verify the external YOLOv8n and OpenPose model assets."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = PROJECT_ROOT / "data" / "public" / "modelos"
OPENPOSE_DIR = MODEL_ROOT / "openpose"
RESULTS_DIR = PROJECT_ROOT / "docs" / "resultados"

OPENPOSE_ASSETS = {
    "pose_deploy.prototxt": {
        "url": (
            "https://raw.githubusercontent.com/CMU-Perceptual-Computing-Lab/"
            "openpose/master/models/pose/coco/pose_deploy_linevec.prototxt"
        ),
        "sha256": "17051b87f709aa094e09c5da7b78e9016a1f37b2b452ed1f190fe74cce70b1ad",
        "license": "OpenPose license; consult the upstream terms before use or redistribution.",
    },
    "pose_iter_440000.caffemodel": {
        "url": (
            "https://posefs1.perception.cs.cmu.edu/OpenPose/models/pose/coco/"
            "pose_iter_440000.caffemodel"
        ),
        "md5": "5156d31f670511fce9b4e28b403f2939",
        "license": "OpenPose license; consult the upstream terms before use or redistribution.",
    },
}


def digest_file(path: Path, algorithm="sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".part")
    request = Request(url, headers={"User-Agent": "fase4-academic-prototype/1.0"})
    try:
        with urlopen(request, timeout=60) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output, 1024 * 1024)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def ensure_openpose_assets() -> list[dict]:
    entries = []
    for name, metadata in OPENPOSE_ASSETS.items():
        target = OPENPOSE_DIR / name
        expected_sha = metadata.get("sha256")
        expected_md5 = metadata.get("md5")
        valid = target.is_file()
        if valid and expected_sha:
            valid = digest_file(target) == expected_sha
        if valid and expected_md5:
            valid = digest_file(target, "md5") == expected_md5
        if not valid:
            target.unlink(missing_ok=True)
            print(f"Obtaining {name} from the OpenPose source...")
            download(metadata["url"], target)
        if expected_sha and digest_file(target) != expected_sha:
            target.unlink(missing_ok=True)
            raise ValueError(f"SHA-256 verification failed for {target.name}.")
        if expected_md5 and digest_file(target, "md5") != expected_md5:
            target.unlink(missing_ok=True)
            raise ValueError(f"MD5 verification failed for {target.name}.")
        entries.append(
            {
                "path": str(target.relative_to(PROJECT_ROOT)),
                "source_url": metadata["url"],
                "license": metadata["license"],
                "bytes": target.stat().st_size,
                "sha256": digest_file(target),
            }
        )
    return entries


def ensure_yolo_asset() -> dict:
    target = MODEL_ROOT / "yolov8n.pt"
    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    if not target.is_file():
        # Ultralytics resolves and downloads this official pretrained checkpoint.
        from ultralytics import YOLO

        model = YOLO("yolov8n.pt")
        downloaded = Path(model.ckpt_path).resolve()
        if not downloaded.is_file():
            raise FileNotFoundError("Ultralytics did not leave a YOLOv8n checkpoint on disk.")
        if downloaded != target.resolve():
            shutil.copy2(downloaded, target)
    return {
        "path": str(target.relative_to(PROJECT_ROOT)),
        "source_url": "https://github.com/ultralytics/assets/releases",
        "model_id": "Ultralytics YOLOv8n, pretrained COCO weights",
        "package_version": "ultralytics==8.3.203",
        "license": "AGPL-3.0 or Ultralytics Enterprise; consult the upstream license.",
        "bytes": target.stat().st_size,
        "sha256": digest_file(target),
    }


def main() -> int:
    entries = ensure_openpose_assets()
    entries.append(ensure_yolo_asset())
    manifest = {
        "description": (
            "Checksums for local model files used by the visual experiments. "
            "Weights are downloaded from their upstream sources and are not stored in Git."
        ),
        "python": sys.version.split()[0],
        "entries": entries,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    target = RESULTS_DIR / "modelos_externos_manifesto.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Model assets are ready. Checksums: {target.relative_to(PROJECT_ROOT)}")
    for entry in entries:
        print(f"- {entry['path']} ({entry['bytes']:,} bytes, SHA-256 {entry['sha256']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
