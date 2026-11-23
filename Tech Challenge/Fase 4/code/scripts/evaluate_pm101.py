"""Avalia seis repetições da gravação PM_101 do REHAB24-6."""

import json, subprocess, sys
from pathlib import Path
import imageio_ffmpeg

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
sys.path.insert(0, str(CODE / "src"))
from fisio_fase4.video import analyze_video

source = ROOT / "data/public/rehab_pm101.mp4"
if not source.exists():
    from remotezip import RemoteZip

    source.parent.mkdir(parents=True, exist_ok=True)
    temporary = source.with_suffix(".mp4.part")
    try:
        with RemoteZip(
            "https://zenodo.org/api/records/13305826/files/videos.zip/content"
        ) as z:
            temporary.write_bytes(z.read("Ex1/PM_101-Camera17-30fps.mp4"))
        temporary.replace(source)
    finally:
        temporary.unlink(missing_ok=True)
rows = []
for i, (first, last) in enumerate(
    [(35, 154), (680, 810), (811, 940), (941, 1065), (1066, 1185), (1186, 1296)]
):
    name = "normal" if i == 0 else f"erro_{i}"
    path = source.parent / f"pm101_{name}.mp4"
    subprocess.run(
        [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-y",
            "-ss",
            str(first / 30),
            "-i",
            str(source),
            "-t",
            str((last - first + 1) / 30),
            "-vf",
            "scale=640:-2",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    result = analyze_video(path, CODE / f"outputs/pm101/{name}.mp4", "pm101")
    rows.append(
        {
            "segment": name,
            "frames": f"{first}-{last}",
            "ground_truth": "correto" if i == 0 else "incorreto",
            "prediction": "desvio" if result["events"] else "sem desvio",
            "max_angle": max((x["angle"] for x in result["angles"]), default=None),
            "pose": f"{result['frames_pose']}/{result['frames_analyzed']}",
        }
    )
path = CODE / "outputs/pm101/resultados.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(rows, ensure_ascii=False, indent=2))
print(json.dumps(rows, ensure_ascii=False, indent=2))
