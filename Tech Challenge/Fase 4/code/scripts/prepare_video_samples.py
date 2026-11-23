"""Recorta repetições anotadas do exercício 1, gravação PM_001, câmera 17."""

from pathlib import Path
import imageio_ffmpeg
import subprocess

ROOT = Path(__file__).resolve().parents[2]
d = ROOT / "data/public"
video = d / "rehab_pm001.mp4"
if not video.exists():
    raise SystemExit("Execute primeiro scripts/download_public_data.py")
for name, first, last in [("correto", 130, 324), ("incorreto", 1690, 1940)]:
    cmd = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-y",
        "-ss",
        str(first / 30),
        "-i",
        str(video),
        "-t",
        str((last - first + 1) / 30),
        "-vf",
        "scale=640:-2",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(d / f"rehab_{name}.mp4"),
    ]
    subprocess.run(
        cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print(name, "quadros", first, "a", last)
