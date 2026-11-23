"""Reduz a velocidade de áudio sintético para demonstrar a regra acústica."""

from pathlib import Path
import subprocess
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[2]
folder = ROOT / "data/public/consultas"
source = folder / "OAW04_consultation.wav"
target = folder / "OAW04_ritmo_simulado.wav"
if not source.exists():
    raise SystemExit("Primeiro execute scripts/download_consultas_rehab26.py")
subprocess.run(
    [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-y",
        "-i",
        str(source),
        "-filter:a",
        "atempo=0.65",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(target),
    ],
    check=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
print("Áudio sintético desacelerado:", target)
