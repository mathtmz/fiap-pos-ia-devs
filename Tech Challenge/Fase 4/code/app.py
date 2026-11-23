from pathlib import Path
import re
import sys
import tempfile

import streamlit as st

CODE = Path(__file__).resolve().parent
ROOT = CODE.parent
sys.path.insert(0, str(CODE / "src"))

from fisio_fase4.pipeline import run_case
from fisio_fase4.replay import replay_events


st.set_page_config(
    page_title="Monitoramento multimodal | Fisioterapia",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.title("Monitoramento multimodal em fisioterapia")
st.caption(
    "Protótipo acadêmico para revisão humana; os alertas não são diagnóstico."
)

st.sidebar.header("Preparar demonstração")
presentation_mode = st.sidebar.checkbox(
    "Modo apresentação: mostrar vídeos e alertas",
    value=True,
    help="Oculta transcrição detalhada, JSON, métricas e informações técnicas da tela principal.",
)
case_id = st.sidebar.text_input("Identificador do caso", "demonstracao_fase4")

source_mode = st.sidebar.radio(
    "Origem das mídias",
    ["Demonstração preparada", "Enviar arquivos próprios"],
    index=0,
)

video = None
audio = None
vitals = None
prescriptions = None
use_samples = True

if source_mode == "Demonstração preparada":
    video_options = {
        "REHAB24-6 · sequência com desvio": (
            ROOT / "data" / "public" / "rehab_incorreto.mp4"
        ),
        "REHAB24-6 · movimento de referência": (
            ROOT / "data" / "public" / "rehab_correto.mp4"
        ),
        "REHAB26-ViewAngles · abdução reduzida": (
            ROOT / "data" / "public" / "rehab26" / "demo_clips" / "low_abduction.mp4"
        ),
        "REHAB26-ViewAngles · cotovelo flexionado": (
            ROOT / "data" / "public" / "rehab26" / "demo_clips" / "bent_arm.mp4"
        ),
        "REHAB26-ViewAngles · ombro elevado": (
            ROOT / "data" / "public" / "rehab26" / "demo_clips" / "shoulder_elevated.mp4"
        ),
        "REHAB26-ViewAngles · inclinação da cabeça": (
            ROOT / "data" / "public" / "rehab26" / "demo_clips" / "head_tilt.mp4"
        ),
    }
    available_videos = {
        label: path for label, path in video_options.items() if path.is_file()
    }
    if available_videos:
        selected_video = st.sidebar.selectbox(
            "Vídeo do exercício",
            list(available_videos),
            index=0,
        )
        video = available_videos[selected_video]
    else:
        st.sidebar.warning(
            "Vídeos de demonstração ausentes. Baixe os materiais conforme o README."
        )

    audio_options = {
        "OAW04 · consulta simulada em português": (
            ROOT / "data" / "public" / "consultas" / "OAW04_consultation.wav"
        ),
        "OAW01 · consulta simulada em português": (
            ROOT / "data" / "public" / "consultas" / "OAW01_consultation.wav"
        ),
    }
    available_audio = {
        label: path for label, path in audio_options.items() if path.is_file()
    }
    if available_audio:
        selected_audio = st.sidebar.selectbox(
            "Áudio da consulta", list(available_audio), index=0
        )
        audio = available_audio[selected_audio]
    else:
        st.sidebar.warning(
            "Áudios de demonstração ausentes. Baixe os materiais conforme o README."
        )

    sample_profile = st.sidebar.selectbox(
        "Sinais e prescrição",
        ["Com alertas (sintéticos)", "Normais (sintéticos)"],
        index=0,
    )
    anomaly_suffix = (
        "anomalia" if sample_profile.startswith("Com alertas") else "normal"
    )
    vitals = ROOT / f"data/synthetic/vitais_{anomaly_suffix}.csv"
    prescriptions = ROOT / f"data/synthetic/prescricoes_{anomaly_suffix}.csv"
    use_samples = False
else:
    video = st.sidebar.file_uploader(
        "Vídeo de exercício", type=["mp4", "mov", "avi"]
    )
    audio = st.sidebar.file_uploader(
        "Áudio de consulta", type=["wav", "mp3", "m4a", "flac"]
    )
    vitals = st.sidebar.file_uploader("Sinais vitais CSV", type=["csv"])
    prescriptions = st.sidebar.file_uploader("Prescrições CSV", type=["csv"])
    use_samples = st.sidebar.checkbox(
        "Usar dados sintéticos de sinais e prescrições", value=True
    )

with st.sidebar.expander("Vídeos exibidos na apresentação", expanded=False):
    show_mediapipe_video = st.checkbox("Mostrar vídeo de movimento", value=True)
    show_pose_video = st.checkbox("Mostrar vídeo com pontos corporais", value=True)

with st.sidebar.expander(
    "Configurações de análise", expanded=not presentation_mode
):
    whisper_model = st.selectbox(
        "Modelo Whisper", ["small", "base", "tiny"], index=0
    )
    use_vad = st.checkbox("VAD experimental (pode cortar fala)", value=False)
    diarize = st.checkbox("Agrupar locutores (experimental)", value=False)
    role_options = ["não identificado", "paciente", "profissional"]
    role_1 = st.selectbox(
        "Papel revisado: locutor 1", role_options, disabled=not diarize
    )
    role_2 = st.selectbox(
        "Papel revisado: locutor 2", role_options, disabled=not diarize
    )
    vision_models = st.checkbox(
        "Executar YOLOv8 e OpenPose ao longo do vídeo", value=True
    )
    vision_fps = st.slider(
        "Amostragem dos modelos visuais (quadros/s)",
        0.5,
        10.0,
        3.0,
        step=0.5,
        key="vision_fps_presentation",
    )
    use_qwen = st.checkbox("Analisar transcrição com Qwen local", value=True)
    st.caption("Na primeira execução, os modelos podem precisar baixar pesos locais.")


def save_upload(upload, destination):
    if not upload:
        return None
    if isinstance(upload, (str, Path)):
        source = Path(upload)
        return source if source.is_file() else None
    path = destination / Path(upload.name).name
    path.write_bytes(upload.getvalue())
    return path


def format_seconds(value):
    return f"{float(value):.0f} s"


def format_alert_evidence(item):
    kind = item.get("kind")
    evidence = str(item.get("evidence", ""))

    if kind == "amplitude_baixa":
        match = re.search(r"max_angle:\s*([\d.]+)°\s+na repetição (.+)", evidence)
        if match:
            angle = match.group(1).replace(".", ",")
            repetition = match.group(2).replace(".", ",")
            return f"{angle}° · repetição {repetition}"
    elif kind == "termo_critico":
        _, _, statement = evidence.partition(":")
        return statement.strip()
    elif kind == "heart_rate":
        _, _, value = evidence.partition(":")
        return value.strip()
    elif kind == "systolic_bp":
        _, _, value = evidence.partition(":")
        return value.strip()
    elif kind == "spo2":
        _, _, value = evidence.partition(":")
        return value.strip()
    elif kind == "variacao_dose":
        _, _, value = evidence.partition(":")
        return value.strip()
    elif kind == "unidade_alterada":
        _, _, value = evidence.partition(":")
        return value.strip()

    return evidence


def render_presentation(result, directory):
    video_info = result["modalities"].get("video", {})
    video_result = video_info.get("result", {})
    extra = video_result.get("modelos_adicionais", {})
    videos = []

    modality_labels = {
        "audio": "áudio de consulta",
        "sinais_vitais": "sinais vitais",
        "prescricoes": "prescrições",
    }
    for modality, label in modality_labels.items():
        status = result["modalities"].get(modality, {}).get("status")
        if status in ("ausente", "erro"):
            st.warning(
                f"Não foi possível analisar {label}. "
                "Confira a entrada antes de gravar."
            )

    if video_info.get("status") == "ok":
        standard_video = directory / "video_anotado.mp4"
        if show_mediapipe_video and standard_video.is_file():
            videos.append(("Movimento analisado", standard_video))
        pose_video = extra.get("annotated_video")
        if (
            show_pose_video
            and pose_video
            and Path(pose_video).is_file()
        ):
            videos.append(("Marcação de pontos corporais", Path(pose_video)))

    if videos:
        st.subheader("Vídeos de resultado")
        columns = st.columns(len(videos))
        for column, (label, path) in zip(columns, videos):
            with column:
                st.markdown(f"**{label}**")
                st.video(str(path), format="video/mp4")
    elif video_info.get("status") == "erro":
        st.warning("O vídeo não pôde ser processado. Confira a entrada antes de gravar.")
    elif video_info.get("status") == "ausente":
        st.warning("Selecione um vídeo de exercício para gerar os resultados visuais.")
    else:
        st.info("Nenhum vídeo de resultado selecionado para este caso.")

    if video_info.get("status") == "ok" and extra.get("status") == "erro":
        st.warning("A marcação de pontos corporais não ficou disponível neste vídeo.")

    st.subheader("Alertas para revisão")
    alerts = result.get("alerts", [])
    if not alerts:
        st.success("Nenhum alerta foi gerado para este caso.")
        return

    st.metric("Alertas", len(alerts))
    modality_labels = {
        "video": "Movimento",
        "texto": "Relato em áudio",
        "sinais_vitais": "Sinais vitais",
        "prescricao": "Prescrição",
    }
    event_labels = {
        "amplitude_baixa": "Amplitude do movimento",
        "cotovelo_flexionado": "Flexão do cotovelo",
        "ombro_elevado": "Elevação do ombro",
        "cabeca_inclinada": "Inclinação da cabeça",
        "braco_fora_do_plano": "Posição do braço",
        "termo_critico": "Relato",
        "heart_rate": "Frequência cardíaca",
        "systolic_bp": "Pressão sistólica",
        "spo2": "Saturação de oxigênio",
        "variacao_dose": "Dose prescrita",
        "unidade_alterada": "Conferir unidade",
    }

    for alert in alerts:
        with st.container(border=True):
            st.markdown(
                f"**Janela {format_seconds(alert['window_start_s'])}–"
                f"{format_seconds(alert['window_end_s'])}**"
            )
            st.caption("Ocorrências agrupadas para revisão humana")
            for item in alert.get("events", []):
                modality = modality_labels.get(item.get("modality"), "Evidência")
                kind = event_labels.get(item.get("kind"), modality)
                evidence = format_alert_evidence(item)
                st.markdown(f"- **{kind}:** {evidence}")


def render_technical_view(result, directory):
    st.subheader("Resultado por modalidade")
    for name, info in result["modalities"].items():
        st.write(f"**{name}:** {info['status']} ({info.get('elapsed_s', 0)} s)")
        if info["status"] == "erro":
            st.error(info["error"])

    audio_info = result["modalities"].get("audio", {})
    if audio_info.get("status") == "ok":
        with st.expander("Transcrição e medidas acústicas", expanded=True):
            st.json(audio_info["result"])

    video_info = result["modalities"].get("video", {})
    if video_info.get("status") == "ok":
        video_result = video_info["result"]
        st.write("Vídeo anotado (MediaPipe):")
        st.video(str(directory / "video_anotado.mp4"), format="video/mp4")
        st.json(
            {
                key: value
                for key, value in video_result.items()
                if key not in ("angles", "measurements", "events")
            }
        )
        extra = video_result.get("modelos_adicionais", {})
        annotated = extra.get("annotated_video")
        if annotated and Path(annotated).is_file():
            st.write("Inspeção temporal YOLOv8 + OpenPose:")
            st.video(annotated, format="video/mp4")
        st.json(
            {
                key: value
                for key, value in extra.items()
                if key not in ("events", "repetitions")
            }
        )
        events_path = extra.get("details_json")
        if events_path and Path(events_path).is_file():
            st.download_button(
                "Baixar pontos e detecções por quadro",
                Path(events_path).read_bytes(),
                file_name="analise_temporal_visao.json",
                mime="application/json",
            )

    st.subheader("Linha do tempo e alertas")
    events = result["events"]
    if events:
        max_time = max(item["time_s"] for item in events)
        cutoff = st.slider(
            "Reproduzir até o instante (s)",
            0,
            max(1, int(max_time) + 1),
            max(1, int(max_time) + 1),
        )
        st.json([item for item in events if item["time_s"] <= cutoff])
        for alert in result["alerts"]:
            if alert["window_start_s"] <= cutoff:
                st.warning(
                    f"Janela {alert['window_start_s']}–{alert['window_end_s']} s: "
                    f"{', '.join(alert['modalities'])}. {alert['message']}"
                )
        if st.button("Reproduzir fluxo de alertas a 1×"):
            area = st.empty()
            summary, _ = replay_events(
                events,
                speed=1.0,
                output_path=directory / "replay_multimodal.jsonl",
                on_event=lambda record: area.warning(
                    f"Alerta em {record['scheduled_time_s']} s — "
                    f"{record['event']['evidence']}"
                ),
            )
            st.json(summary)
            st.caption("Reprodução local; análise calculada previamente.")
    else:
        st.info("Nenhum evento detectado nas modalidades processadas.")

    st.download_button(
        "Baixar relatório JSON",
        (directory / "relatorio.json").read_bytes(),
        file_name="relatorio.json",
        mime="application/json",
    )
    st.caption(
        f"Tempo de processamento: {result['processing_elapsed_s']} s. "
        "A linha do tempo é uma reprodução, não monitoramento contínuo."
    )


if st.button("Processar caso", type="primary"):
    if not case_id.strip():
        st.error("Informe um identificador para o caso.")
    else:
        temporary = Path(tempfile.mkdtemp(prefix="fisio_fase4_"))
        sources = {
            "video": save_upload(video, temporary),
            "audio": save_upload(audio, temporary),
            "vitals": save_upload(vitals, temporary),
            "prescriptions": save_upload(prescriptions, temporary),
        }
        if use_samples:
            sources["vitals"] = (
                sources["vitals"] or ROOT / "data/synthetic/vitais_anomalia.csv"
            )
            sources["prescriptions"] = (
                sources["prescriptions"]
                or ROOT / "data/synthetic/prescricoes_anomalia.csv"
            )
        with st.spinner("Preparando os resultados do caso..."):
            result = run_case(
                case_id.strip(),
                temporary / "resultados",
                qwen=use_qwen,
                whisper_model=whisper_model,
                use_vad=use_vad,
                diarize=diarize,
                vision_models=vision_models,
                vision_fps=float(vision_fps),
                speaker_roles={"locutor_1": role_1, "locutor_2": role_2},
                **sources,
            )
        st.session_state["result"] = result
        st.session_state["result_dir"] = str(temporary / "resultados")


if "result" in st.session_state:
    result = st.session_state["result"]
    result_directory = Path(st.session_state["result_dir"])
    if presentation_mode:
        render_presentation(result, result_directory)
    else:
        render_technical_view(result, result_directory)
else:
    st.info(
        "A demonstração está preparada. Selecione **Processar caso** para gerar "
        "os vídeos e alertas."
    )
