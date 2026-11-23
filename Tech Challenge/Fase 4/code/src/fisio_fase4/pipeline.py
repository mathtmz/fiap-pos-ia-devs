"""Orquestração com modalidades opcionais e estado explícito de falha."""

import csv
import time
from pathlib import Path
from .analysis import (
    detect_vitals,
    detect_prescriptions,
    fuse_events,
    refresh_event_id,
    write_json,
)


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def run_case(
    case_id,
    output_dir,
    vitals=None,
    prescriptions=None,
    video=None,
    audio=None,
    qwen=True,
    whisper_model="small",
    use_vad=False,
    diarize=False,
    speaker_roles=None,
    vision_models=True,
    vision_fps=5.0,
):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    results = {}
    events = []

    def execute(name, source, fn):
        if not source:
            results[name] = {"status": "ausente"}
            return
        before = time.perf_counter()
        try:
            value = fn()
            for item in value.get("events", []):
                if not item.get("source"):
                    item["source"] = Path(source).name
                refresh_event_id(item)
            results[name] = {
                "status": "ok",
                "elapsed_s": round(time.perf_counter() - before, 3),
                "result": value,
            }
            events.extend(value.get("events", []))
        except Exception as exc:
            results[name] = {
                "status": "erro",
                "error": f"{type(exc).__name__}: {exc}",
                "elapsed_s": round(time.perf_counter() - before, 3),
            }

    def clinical(fn, source):
        return {"events": fn(read_csv(source), case_id)}

    execute("sinais_vitais", vitals, lambda: clinical(detect_vitals, vitals))
    execute(
        "prescricoes",
        prescriptions,
        lambda: clinical(detect_prescriptions, prescriptions),
    )

    def video_fn():
        from .video import analyze_video

        value = analyze_video(
            video,
            output / "video_anotado.mp4",
            case_id,
            thresholds={"max_angle": 132.35},
        )
        if vision_models:
            try:
                from .vision_models import analyze_video_models, DEFAULT_THRESHOLDS

                detailed = analyze_video_models(
                    video,
                    output / "modelos_visao",
                    Path(__file__).resolve().parents[3]
                    / "data/public/modelos/openpose",
                    case_id=case_id,
                    sample_fps=vision_fps,
                    thresholds=DEFAULT_THRESHOLDS,
                    write_video=True,
                )
                detailed_path = output / "modelos_visao" / "analise_temporal.json"
                write_json(detailed_path, detailed)
                value["events"].extend(detailed.get("events", []))
                value["modelos_adicionais"] = {
                    key: item
                    for key, item in detailed.items()
                    if key not in ("frames_data",)
                }
                value["modelos_adicionais"]["details_json"] = str(detailed_path)
            except Exception as exc:
                value["modelos_adicionais"] = {
                    "status": "erro",
                    "error": f"{type(exc).__name__}: {exc}",
                }
        return value

    execute("video", video, video_fn)

    def audio_fn():
        from .audio_text import (
            transcribe,
            acoustic_features,
            analyze_segments,
            vocal_screening,
        )
        import imageio_ffmpeg, subprocess

        wav = output / "audio_convertido.wav"
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-y",
                "-i",
                str(audio),
                "-ac",
                "1",
                "-ar",
                "16000",
                str(wav),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        transcription = transcribe(
            wav, model_name=whisper_model, language="pt", use_vad=use_vad
        )
        features = acoustic_features(wav, transcription["text"])
        diarization = {"status": "desativado"}
        if diarize:
            try:
                from .diarization import cluster_speakers

                diarization = cluster_speakers(wav, transcription["segments"])
                transcription["segments"] = diarization["segments"]
                for segment in transcription["segments"]:
                    segment["role"] = (speaker_roles or {}).get(
                        segment["speaker"], "não identificado"
                    )
            except Exception as exc:
                diarization = {
                    "status": "erro",
                    "error": f"{type(exc).__name__}: {exc}",
                }
        screening = vocal_screening(features, case_id)
        value = {
            "transcription": transcription,
            "acoustics": features,
            "diarization": diarization,
            "vocal_screening": screening,
            "configuration": {
                "whisper_model": whisper_model,
                "language": "pt",
                "vad": use_vad,
                "diarization_enabled": diarize,
                "qwen_enabled": qwen,
                "qwen_model": (
                    "Qwen/Qwen2.5-0.5B-Instruct" if qwen else None
                ),
            },
            "events": list(screening["events"]),
        }
        if qwen:
            try:
                analysis = analyze_segments(transcription["segments"], case_id)
                value["text_analysis"] = analysis
                value["events"].extend(analysis["events"])
            except Exception as exc:
                value["text_analysis"] = {
                    "status": "erro",
                    "error": f"{type(exc).__name__}: {exc}",
                }
        else:
            value["text_analysis"] = {"status": "desativado"}
        return value

    execute("audio", audio, audio_fn)
    payload = {
        "case_id": case_id,
        "modalities": results,
        "events": events,
        "alerts": fuse_events(events),
        "processing_elapsed_s": round(time.perf_counter() - start, 3),
        "notice": "Protótipo acadêmico; dados associados artificialmente e critérios não validados clinicamente.",
    }
    write_json(output / "relatorio.json", payload)
    return payload
