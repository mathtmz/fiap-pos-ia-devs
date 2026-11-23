import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from fisio_fase4.analysis import detect_vitals, detect_prescriptions, fuse_events
from fisio_fase4.pipeline import run_case


def test_vital_thresholds_and_missing():
    events = detect_vitals(
        [
            {
                "time_s": 1,
                "heart_rate": 121,
                "spo2": "",
                "systolic_bp": 120,
                "diastolic_bp": 80,
            }
        ],
        "a",
    )
    assert len(events) == 1 and events[0]["kind"] == "heart_rate"
    assert detect_vitals([{"time_s": 2, "heart_rate": 120}], "a") == []


def test_prescription_unit_change_not_numeric_comparison():
    rows = [
        {"time_s": 0, "medication": "X", "dose": 10, "unit": "mg"},
        {"time_s": 2, "medication": "X", "dose": 20, "unit": "mg"},
        {"time_s": 4, "medication": "X", "dose": 20, "unit": "mcg"},
    ]
    assert [e["kind"] for e in detect_prescriptions(rows, "a")] == [
        "variacao_dose",
        "unidade_alterada",
    ]


def test_fusion_case_and_window():
    es = detect_vitals(
        [{"time_s": 5, "heart_rate": 130}, {"time_s": 35, "heart_rate": 130}], "a"
    )
    es += detect_vitals([{"time_s": 5, "heart_rate": 130}], "b")
    alerts = fuse_events(es, 30)
    assert [(a["case_id"], a["window_start_s"]) for a in alerts] == [
        ("a", 0),
        ("a", 30),
        ("b", 0),
    ]
    assert alerts[0]["events"][0]["evidence"]


def test_pipeline_missing_and_invalid(tmp_path):
    result = run_case("a", tmp_path / "out", vitals=tmp_path / "inexistente.csv")
    assert result["modalities"]["sinais_vitais"]["status"] == "erro"
    assert result["modalities"]["video"]["status"] == "ausente"
    assert (tmp_path / "out" / "relatorio.json").exists()


def test_text_events_only_matching_segment():
    from fisio_fase4.audio_text import text_events

    found = text_events(
        {"terms": ["dor", "inexistente"]}, [{"start": 1, "text": "sinto dor aqui"}], "a"
    )
    assert len(found) == 1 and found[0]["time_s"] == 1


def test_unavailable_text_model_reported_without_losing_transcript(
    tmp_path, monkeypatch
):
    import fisio_fase4.audio_text as audio_text
    import imageio_ffmpeg, subprocess

    monkeypatch.setattr(imageio_ffmpeg, "get_ffmpeg_exe", lambda: "ffmpeg")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        audio_text,
        "transcribe",
        lambda path, **kwargs: {
            "text": "fala",
            "segments": [{"start": 0, "end": 1, "text": "fala"}],
            "language": "pt",
        },
    )
    monkeypatch.setattr(
        audio_text, "acoustic_features", lambda path, text: {"duration_s": 1}
    )

    def fail(text):
        raise RuntimeError("modelo indisponível")

    monkeypatch.setattr(audio_text, "analyze_text", fail)
    result = run_case("a", tmp_path / "out", audio="amostra.wav")
    audio = result["modalities"]["audio"]
    assert audio["status"] == "ok"
    assert audio["result"]["text_analysis"]["status"] == "erro"
    assert audio["result"]["transcription"]["text"] == "fala"


def test_video_cannot_open_is_reported(tmp_path):
    result = run_case("a", tmp_path / "out", video=tmp_path / "nao_existe.mp4")
    assert result["modalities"]["video"]["status"] == "erro"
    assert result["alerts"] == []


def test_text_events_word_boundary():
    from fisio_fase4.audio_text import text_events

    segments = [
        {"start": 1, "text": "um ador em coma"},
        {"start": 3, "text": "por causa da dor."},
    ]
    found = text_events({"terms": ["dor"]}, segments, "a")
    assert len(found) == 1 and found[0]["time_s"] == 3


def test_chunk_analysis_covers_all_segments_and_marks_questions(monkeypatch):
    import fisio_fase4.audio_text as module

    calls = []

    def analyze(text):
        calls.append(text)
        return {
            "status": "ok",
            "sentiment": "neutro",
            "terms": ["dor"] if "dor" in text else [],
        }

    monkeypatch.setattr(module, "analyze_text", analyze)
    segments = [
        {"start": 0, "end": 1, "text": "Você sente dor?"},
        {"start": 2, "end": 3, "text": "Outra frase"},
    ]
    result = module.analyze_segments(segments, "a", chunk_size=12)
    assert len(calls) == 2 and result["chunks"][-1]["end"] == 3
    assert result["review_items"][0]["review_status"] == "revisar_negacao_ou_pergunta"
    assert result["review_items"][0]["speaker"] == "não identificado"


def test_shoulder_angle_accounts_for_aspect_ratio():
    from types import SimpleNamespace as P
    from fisio_fase4.video import shoulder_angle

    a = shoulder_angle(P(x=0, y=0), P(x=1, y=1), P(x=0, y=1), 2)
    assert 63 < a < 64


def test_vad_silence_is_explicit(monkeypatch):
    import numpy as np
    import whisper
    import faster_whisper.vad as vad
    from fisio_fase4.audio_text import transcribe

    monkeypatch.setenv("PATH", str(Path(sys.executable).parent))
    monkeypatch.setattr(whisper, "load_model", lambda *args, **kwargs: object())
    monkeypatch.setattr(
        whisper, "load_audio", lambda path: np.zeros(16000, dtype=np.float32)
    )
    monkeypatch.setattr(vad, "get_speech_timestamps", lambda audio: [])
    result = transcribe("silencio.wav", language="pt", use_vad=True)
    assert result["segments"] == [] and result["vad_status"] == "sem fala detectada"


def test_repetition_segmentation_and_calibrated_events():
    from fisio_fase4.repetitions import summarize_repetitions, evaluate_repetitions

    angles = [
        {"time_s": i * 0.1, "angle": a, "side": "direito"}
        for i, a in enumerate([10, 15, 35, 50, 70, 80, 60, 35, 20, 10])
    ]
    measurements = [
        {"time_s": x["time_s"], "side": "direito", "elbow_angle": 120, "trunk_tilt": 10}
        for x in angles
    ]
    reps = summarize_repetitions(angles, measurements)
    assert len(reps) == 1 and reps[0]["status"] == "avaliavel"
    evaluate_repetitions(reps, {"min_elbow_angle": 130}, "a")
    assert reps[0]["events"][0]["kind"] == "cotovelo_flexionado"


def test_diarization_without_speech_is_inconclusive(tmp_path):
    import numpy as np, soundfile as sf
    from fisio_fase4.diarization import cluster_speakers

    path = tmp_path / "silence.wav"
    sf.write(path, np.zeros(16000), 16000)
    out = cluster_speakers(path, [{"start": 0, "end": 1, "text": "teste"}])
    assert (
        out["status"] == "inconclusivo"
        and out["segments"][0]["speaker"] == "não identificado"
    )


def test_repeated_text_term_keeps_each_timestamp():
    from fisio_fase4.audio_text import text_events

    segments = [
        {"start": 1, "text": "dor no joelho"},
        {"start": 5, "text": "dor no braço"},
    ]
    assert [e["time_s"] for e in text_events({"terms": ["dor"]}, segments, "a")] == [
        1,
        5,
    ]


def test_vocal_screening_is_exploratory():
    from fisio_fase4.audio_text import vocal_screening

    result = vocal_screening(
        {"duration_s": 30, "words_per_minute": 60, "silent_frame_fraction": 0.7}, "caso"
    )
    assert (
        result["status"] == "avaliado_experimental"
        and result["events"][0]["modality"] == "audio"
    )
    assert (
        vocal_screening(
            {"duration_s": 3, "words_per_minute": 60, "silent_frame_fraction": 0.7},
            "caso",
        )["status"]
        == "inconclusivo"
    )
