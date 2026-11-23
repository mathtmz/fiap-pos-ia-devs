"""Agrupamento acústico experimental em segmentos existentes, sem identificação de pessoas."""


def cluster_speakers(audio_path, segments, num_speakers=2):
    import numpy as np
    import soundfile as sf
    from python_speech_features import mfcc
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    audio, rate = sf.read(str(audio_path), always_2d=True)
    mono = audio.mean(axis=1)
    features = []
    indices = []
    for i, s in enumerate(segments):
        start = max(0, int(s["start"] * rate))
        end = min(len(mono), int(s["end"] * rate))
        piece = mono[start:end]
        if len(piece) < rate * 0.6 or np.sqrt(np.mean(piece**2)) < 0.002:
            continue
        coefficients = mfcc(
            piece, rate, numcep=13, nfilt=26, nfft=1024 if rate <= 16000 else 2048
        )
        features.append(np.r_[coefficients.mean(axis=0), coefficients.std(axis=0)])
        indices.append(i)
    result = [
        dict(s, speaker="não identificado", role="não identificado") for s in segments
    ]
    if len(features) < max(4, num_speakers * 2):
        return {
            "status": "inconclusivo",
            "segments": result,
            "reason": "fala insuficiente para agrupamento",
        }
    x = StandardScaler().fit_transform(features)
    if np.max(np.std(x, axis=0)) < 1e-6:
        return {
            "status": "inconclusivo",
            "segments": result,
            "reason": "segmentos sem variação suficiente",
        }
    labels = KMeans(n_clusters=num_speakers, random_state=42, n_init=10).fit_predict(x)
    for i, label in zip(indices, labels):
        result[i]["speaker"] = f"locutor_{label+1}"
    return {
        "status": "experimental",
        "segments": result,
        "reason": "MFCC e agrupamento em dois grupos; sem identificação automática de papéis e sem validação de diarização",
    }
