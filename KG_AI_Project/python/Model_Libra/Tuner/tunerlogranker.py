import json
from datetime import datetime
from pathlib import Path
from collections import OrderedDict

class TunerLogRanker:
    def __init__(self, log_dir: Path, model_num: str, timestamp: str):
        self.log_dir = log_dir
        self.model_num = model_num
        self.timestamp = timestamp  # 메인에서 받아온 타임스탬프

    def load_trials(self) -> list:
        trial_logs = []
        for path in self.log_dir.glob(f"{self.model_num}_Tuner_Log_*.json"):
            with open(path, "r", encoding="utf-8") as f:
                logs = json.load(f)
                trial_logs.extend(logs)
        return trial_logs

    def filter_and_rank_trials(self, logs: list, top_k: int = 5) -> list:
        def ranking_key(trial):
            score = trial.get("summary_metrics", {}).get("cluster_test", {})
            cluster_R2 = score.get("R2", -1)
            predict_R2 = trial.get("summary_metrics", {}).get("full_predict", {}).get("R2", -1)
            std = trial.get("mean_rank_stddev", 99999)
            error = trial.get("rank_error_score", 999999999)
            better = trial.get("cluster_better_than_predict", False)
            return (
                std,
                error,
                -cluster_R2,
                -predict_R2,
                not better
            )

        filtered = [t for t in logs if t.get("summary_metrics", {}).get("cluster_test", {}).get("R2", 0) >= 0.8]
        ranked = sorted(filtered, key=ranking_key)
        return ranked[:top_k]

    def save_rating_log(self, ranked_trials: list, cycle_idx: int):
        reordered_trials = []
        for i, trial in enumerate(ranked_trials, start=1):
            # rank와 timestamp 분리
            rank_value = i
            timestamp_value = trial.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # rank → timestamp → 나머지 순서 보장
            ordered_trial = OrderedDict()
            ordered_trial["rank"] = rank_value
            ordered_trial["timestamp"] = timestamp_value

            for key, value in trial.items():
                if key not in ["rank", "timestamp"]:
                    ordered_trial[key] = value

            reordered_trials.append(ordered_trial)

        rating = {
            "timestamp": datetime.now().isoformat(),
            "cycle": cycle_idx,
            "ranked_trials": reordered_trials
        }

        path = self.log_dir / f"{self.model_num}_TopRating_{self.timestamp}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rating, f, indent=2)

    def rank_top_trials(self, top_k: int = 5) -> list:
        def score_key(trial):
            cluster_r2 = trial.get("cluster_R2", -1)
            mean_std = trial.get("mean_rank_stddev", 99999)
            error_score = trial.get("rank_error_score", 99999999)
            full_r2 = trial.get("full_predict_R2", -1)
            better = trial.get("cluster_better_than_predict", False)
            return (
                mean_std,
                error_score,
                -cluster_r2,
                -full_r2,
                not better
            )

        logs = self.load_trials()
        filtered = [trial for trial in logs if trial.get("cluster_R2", 0) >= 0.8]
        ranked = sorted(filtered, key=score_key)
        return ranked[:top_k]
