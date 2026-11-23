"""Make imageio-ffmpeg available under the command name expected by Whisper."""

import os
from pathlib import Path
import shutil
import sys

import imageio_ffmpeg

source = Path(imageio_ffmpeg.get_ffmpeg_exe())
target_dir = Path(sys.prefix) / ("Scripts" if os.name == "nt" else "bin")
target = target_dir / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
target_dir.mkdir(parents=True, exist_ok=True)
if not target.exists():
    try:
        target.symlink_to(source)
    except OSError:
        shutil.copy2(source, target)
        if os.name != "nt":
            target.chmod(target.stat().st_mode | 0o111)
print(f"FFmpeg disponível em {target}")
