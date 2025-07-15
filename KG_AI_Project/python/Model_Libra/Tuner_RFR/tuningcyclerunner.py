# Tuner_RFR/tuningcyclerunner.py

import subprocess
import json
from core_utiles.config_loader import RFR_CONFIG_PATH
from pathlib import Path

def run_ml_rfr_pipeline():
    entrypoint = Path(RFR_CONFIG_PATH) / "__main__.py"
    subprocess.run(["python", str(entrypoint)], check=True)


def get_latest_metrics(metrics_path: Path) -> dict:
    try:
        with open(metrics_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
