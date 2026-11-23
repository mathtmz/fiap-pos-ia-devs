import importlib.util
from pathlib import Path

script = Path(__file__).resolve().parents[1] / "scripts" / "monitor_stream.py"
spec = importlib.util.spec_from_file_location("monitor_stream", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_stream_emits_new_prescription_event_once(tmp_path):
    vitals = tmp_path / "v.csv"
    vitals.write_text("time_s,heart_rate\n0,80\n1,130\n")
    prescriptions = tmp_path / "p.csv"
    prescriptions.write_text(
        "time_s,medication,dose,unit\n0,a,10,mg\n1,a,20,mg\n2,a,20,mg\n"
    )
    output = list(module.monitor(vitals, prescriptions, speed=10000))
    kinds = [event["kind"] for row in output for event in row["events"]]
    assert kinds.count("variacao_dose") == 1 and kinds.count("heart_rate") == 1
