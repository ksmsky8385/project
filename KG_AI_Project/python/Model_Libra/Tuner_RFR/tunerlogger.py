# Tuner_RFR/tunerlogger.py

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class TunerLogger:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log = self._load_log()

    def _load_log(self) -> List[Dict[str, Any]]:
        try:
            if not self.log_path.exists() or self.log_path.stat().st_size == 0:
                return []
            with open(self.log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def append_cycle(self, n_clusters: int, cluster_params: dict, summary_metrics: dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "n_clusters": n_clusters,
            "cluster_params": cluster_params,
            "summary_metrics": summary_metrics
        }
        self.log.append(entry)
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2)
