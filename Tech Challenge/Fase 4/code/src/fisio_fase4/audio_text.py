"""Transcrição local, medidas acústicas e extração textual baseada em Qwen."""

from __future__ import annotations
import json
import os
import re
import shutil
import sys
from functools import lru_cache
from pathlib import Path
from .analysis import event


def acoustic_features(audio_path, transcript=""):
    import numpy as np
    import soundfile as sf

    samples, rate = sf.read(str(audio_path), always_2d=True)
    mono = samples.mean(axis=1)
    if not len(mono):
        raise ValueError("Áudio vazio.")
    duration = len(mono) / rate
    frame = max(1, int(rate * 0.03))
    rms = []
    for i in range(0, len(mono), frame):
        chunk = mono[i : i + frame]
        rms.append(float(np.sqrt(np.mean(chunk * chunk))))
    peak = max(rms) if rms else 0
    threshold = max(0.005, peak * 0.1)
    silent = sum(x < threshold for x in rms) / len(rms) if rms else 0
    words = len(re.findall(r"\b\w+\b", transcript, flags=re.UNICODE))
    return {
        "duration_s": round(duration, 2),
        "silent_frame_fraction": round(silent, 3),
        "words_per_minute": round(words / duration * 60, 1),
        "rms_threshold": round(threshold, 5),
        "limitation": "Medidas descritivas; silêncio e ritmo não diagnosticam fadiga ou dispneia.",
    }


def transcribe(path, model_name="small", language=None, use_vad=False):
    import imageio_ffmpeg
    import whisper

    ffmpeg_dir = Path(sys.prefix) / ("Scripts" if os.name == "nt" else "bin")
    executable_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    alias = ffmpeg_dir / executable_name
    if alias.exists() and str(ffmpeg_dir) not in os.environ.get("PATH", "").split(os.pathsep):
        os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")
    if shutil.which("ffmpeg") is None:
        ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe())
        raise RuntimeError(
            "FFmpeg is not available in PATH. Run "
            f"python {Path(__file__).resolve().parents[2] / 'scripts' / 'setup_ffmpeg.py'} "
            f"inside the project environment (bundled binary: {ffmpeg})."
        )
    model = whisper.load_model(model_name, device="cpu")
    clips = "0"
    if use_vad:
        from faster_whisper.vad import get_speech_timestamps

        speech = get_speech_timestamps(whisper.load_audio(str(path)))
        if not speech:
            return {
                "text": "",
                "language": language or "indeterminado",
                "segments": [],
                "vad_status": "sem fala detectada",
            }
        # Agrupar trechos próximos preserva pausas curtas e reduz cortes de fala.
        merged = []
        for region in speech:
            if merged and region["start"] - merged[-1]["end"] <= 32000:
                merged[-1]["end"] = region["end"]
            else:
                merged.append(dict(region))
        clips = [
            boundary / 16000
            for region in merged
            for boundary in (region["start"], region["end"])
        ]
    result = model.transcribe(
        str(path),
        language=language,
        fp16=False,
        verbose=False,
        temperature=0,
        condition_on_previous_text=False,
        clip_timestamps=clips,
    )
    return {
        "text": result["text"].strip(),
        "language": result["language"],
        "segments": [
            {
                "start": round(x["start"], 2),
                "end": round(x["end"], 2),
                "text": x["text"].strip(),
            }
            for x in result["segments"]
        ],
        "vad_status": "ativo" if use_vad else "inativo",
    }


def literal_match(term, text):
    return bool(
        re.search(
            r"(?<!\w)" + re.escape(term.strip()) + r"(?!\w)", text, flags=re.IGNORECASE
        )
    )


@lru_cache(maxsize=1)
def _load_language_model(model_name):
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    config = AutoConfig.from_pretrained(model_name)
    # Transformers 4.51 warns whenever this field is set, even when the Qwen
    # config explicitly disables sliding-window attention. Removing the unused
    # value avoids that misleading warning without changing the model behavior.
    if hasattr(config, "use_sliding_window") and not config.use_sliding_window:
        config.sliding_window = None
    return AutoTokenizer.from_pretrained(
        model_name
    ), AutoModelForCausalLM.from_pretrained(
        model_name,
        config=config,
        torch_dtype=torch.float32,
        attn_implementation="eager",
    )


def analyze_text(text, model_name="Qwen/Qwen2.5-0.5B-Instruct"):
    import torch

    tokenizer, model = _load_language_model(model_name)
    messages = [
        {
            "role": "system",
            "content": "Você analisa relato de fisioterapia para estudo. Responda apenas JSON com sentiment (positivo, negativo ou neutro) e terms (lista de trechos literais que indicam dor, cansaço, falta de ar ou sintomas). Não invente termos nem dê diagnóstico.",
        },
        {"role": "user", "content": text[:4000]},
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer([prompt], return_tensors="pt")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=180,
            do_sample=False,
            temperature=1.0,
            top_p=1.0,
            top_k=50,
            pad_token_id=tokenizer.eos_token_id,
        )
    raw = tokenizer.decode(
        output[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
    ).strip()
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
        sentiment = parsed.get("sentiment", "indeterminado")
        sentiment = {
            "positive": "positivo",
            "negative": "negativo",
            "neutral": "neutro",
        }.get(str(sentiment).lower(), str(sentiment).lower())
        if sentiment not in ("positivo", "negativo", "neutro"):
            sentiment = "indeterminado"
        terms = parsed.get("terms", [])
        if not isinstance(terms, list):
            terms = []
        allowed = (
            "dor",
            "cansaço",
            "cansaco",
            "fadiga",
            "falta de ar",
            "dispneia",
            "dificuldade de respirar",
            "pain",
            "fatigue",
            "shortness of breath",
            "breathless",
        )
        terms = [
            t.strip()
            for t in terms
            if isinstance(t, str)
            and t.strip()
            and literal_match(t, text)
            and any(literal_match(word, t) for word in allowed)
        ]
        return {
            "sentiment": sentiment,
            "terms": terms,
            "raw_output": raw,
            "status": "ok",
        }
    except (ValueError, TypeError, AttributeError):
        return {
            "sentiment": "indeterminado",
            "terms": [],
            "raw_output": raw,
            "status": "formato_invalido",
        }


def text_events(analysis, segments, case_id):
    events = []
    for term in dict.fromkeys(analysis.get("terms", [])):
        for segment in segments:
            if not literal_match(term, segment["text"]):
                continue
            item = event(
                case_id,
                segment["start"],
                "texto",
                "termo_critico",
                f'{term}: {segment["text"]}',
                "Termo literal selecionado pelo modelo, sujeito à revisão",
            )
            item["speaker"] = segment.get("speaker", "não identificado")
            item["role"] = segment.get("role", "não identificado")
            events.append(item)
    return events


def route_text_events(analysis, segments, case_id):
    """Route literal model terms to alerts or human review by sentence context."""
    events, review_items = [], []
    for item in text_events(analysis, segments, case_id):
        sentence = item["evidence"].split(": ", 1)[-1].casefold()
        if "?" in sentence or re.search(r"\b(?:sem|nega|não|nao)\b", sentence):
            item["review_status"] = "revisar_negacao_ou_pergunta"
            review_items.append(item)
        else:
            item["review_status"] = "revisao_pendente"
            events.append(item)
    return events, review_items


def analyze_segments(segments, case_id, chunk_size=3000):
    """Analisa todos os segmentos; locutores não inferidos sem diarização."""
    groups = []
    group = []
    size = 0
    for segment in segments:
        if group and size + len(segment["text"]) > chunk_size:
            groups.append(group)
            group = []
            size = 0
        group.append(segment)
        size += len(segment["text"])
    if group:
        groups.append(group)
    chunks = []
    events = []
    review_items = []
    for group in groups:
        analysis = analyze_text(" ".join(x["text"] for x in group))
        chunk_events, chunk_reviews = route_text_events(analysis, group, case_id)
        events.extend(chunk_events)
        review_items.extend(chunk_reviews)
        chunks.append(
            {"start": group[0]["start"], "end": group[-1]["end"], "analysis": analysis}
        )
    return {
        "status": "ok",
        "chunks": chunks,
        "speaker_status": (
            "agrupamento experimental"
            if any(
                x.get("speaker", "não identificado") != "não identificado"
                for x in segments
            )
            else "não identificado"
        ),
        "events": events,
        "review_items": review_items,
    }


def vocal_screening(features, case_id):
    """Sinaliza medidas atípicas apenas como triagem exploratória.

    Limites arbitrários; não reconhece fadiga, disartria ou dispneia.
    """
    findings = []
    if features["duration_s"] < 10 or features["words_per_minute"] == 0:
        return {
            "status": "inconclusivo",
            "events": [],
            "reason": "Áudio curto ou sem transcrição.",
        }
    if features["words_per_minute"] < 80 and features["silent_frame_fraction"] > 0.5:
        findings.append(
            event(
                case_id,
                0,
                "audio",
                "padrao_vocal_exploratorio",
                f"{features['words_per_minute']} palavras/min; {features['silent_frame_fraction']:.1%} quadros silenciosos",
                "Regra arbitrária: <80 palavras/min e >50% quadros silenciosos; revisão humana necessária",
            )
        )
    return {
        "status": "avaliado_experimental",
        "events": findings,
        "reason": "Não constitui detecção clínica nem identifica causas.",
    }
