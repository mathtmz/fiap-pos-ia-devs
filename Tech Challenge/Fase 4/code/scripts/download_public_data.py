"""Baixa somente um vídeo e metadados do REHAB24-6; confira a licença antes de usar."""

from pathlib import Path
from urllib.request import urlretrieve
from remotezip import RemoteZip

ROOT = Path(__file__).resolve().parents[2]
dest = ROOT / "data/public"
dest.mkdir(parents=True, exist_ok=True)
base = "https://zenodo.org/api/records/13305826/files/"
for name in ["Segmentation.csv", "Segmentation.txt"]:
    target = dest / name
    if not target.exists():
        urlretrieve(base + name + "/content", target)
target = dest / "rehab_pm001.mp4"
if not target.exists():
    with RemoteZip(base + "videos.zip/content") as z:
        target.write_bytes(z.read("Ex1/PM_001-Camera17-30fps.mp4"))
jfk = dest / "jfk.flac"
if not jfk.exists():
    urlretrieve(
        "https://raw.githubusercontent.com/openai/whisper/main/tests/jfk.flac", jfk
    )
print("Fontes baixadas em", dest)
