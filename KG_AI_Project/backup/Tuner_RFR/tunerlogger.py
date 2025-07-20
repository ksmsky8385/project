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

    def append_cycle(
        self,
        n_clusters,
        cluster_params,
        summary_metrics,
        rank_error_score=None,
        rank_error_by_year=None,
        rank_stddev_by_year=None,
        mean_rank_stddev=None
    ):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "n_clusters": n_clusters,
            "cluster_params": cluster_params,
            "summary_metrics": summary_metrics,
        }
        if rank_error_score is not None:
            entry["rank_error_score"] = rank_error_score
        if rank_error_by_year is not None:
            entry["rank_error_by_year"] = rank_error_by_year
        if rank_stddev_by_year is not None:
            entry["rank_stddev_by_year"] = rank_stddev_by_year
        if mean_rank_stddev is not None:
            entry["mean_rank_stddev"] = mean_rank_stddev

        self.log.append(entry)
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2)


