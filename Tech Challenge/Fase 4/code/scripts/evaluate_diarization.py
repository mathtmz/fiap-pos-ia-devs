"""Evaluate experimental speaker grouping on the synthetic OAW04 reference."""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path


CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent


def tokenize(text):
    return re.findall(r"\w+", text.casefold())


def evaluate():
    reference = json.loads(
        (PROJECT_ROOT / "data/public/consultas/OAW04_transcript.json").read_text(
            encoding="utf-8"
        )
    )
    report_path = CODE_DIR / "outputs/diarizacao_experimental/relatorio.json"
    if not report_path.is_file():
        raise FileNotFoundError(
            "Run run_demo.py with --diarize on OAW04 before this evaluation."
        )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    segments = report["modalities"]["audio"]["result"]["transcription"]["segments"]
    reference_words = [
        (word, turn["speaker"])
        for turn in reference
        for word in tokenize(turn["text"])
    ]
    hypothesis_words = [
        (word, segment.get("speaker", "não identificado"))
        for segment in segments
        for word in tokenize(segment["text"])
    ]
    aligned = []
    matcher = SequenceMatcher(
        None,
        [word for word, _ in reference_words],
        [word for word, _ in hypothesis_words],
        autojunk=False,
    )
    for operation, ref_start, ref_end, hyp_start, hyp_end in matcher.get_opcodes():
        if operation == "equal":
            aligned.extend(
                (reference_words[ref_start + offset][1], hypothesis_words[hyp_start + offset][1])
                for offset in range(ref_end - ref_start)
            )

    known = [
        (expected, actual)
        for expected, actual in aligned
        if actual in ("locutor_1", "locutor_2")
    ]
    mappings = (
        {"locutor_1": "patient", "locutor_2": "doctor"},
        {"locutor_1": "doctor", "locutor_2": "patient"},
    )
    correct_counts = [
        sum(mapping[actual] == expected for expected, actual in known)
        for mapping in mappings
    ]
    result = {
        "dataset": "OAW04 synthetic consultation",
        "reference_words": len(reference_words),
        "transcribed_words": len(hypothesis_words),
        "aligned_words": len(aligned),
        "aligned_words_with_cluster": len(known),
        "speaker_accuracy_best_mapping": (
            round(max(correct_counts) / len(known), 4) if known else None
        ),
        "mapping_selected_using_reference": True,
        "limitation": (
            "One synthetic consultation; word-aligned cluster accuracy after "
            "choosing the better speaker mapping. This is not diarization error rate."
        ),
    }
    output = PROJECT_ROOT / "docs/resultados/diarizacao_sintetica.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
