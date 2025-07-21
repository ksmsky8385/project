import json
from pathlib import Path
from datetime import datetime

class TunerLogger:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log = []

        # 로그 파일이 존재하면 기존 내용 로딩
        if self.log_path.exists():
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    self.log = json.load(f)
            except Exception as e:
                print(f"[경고] 기존 로그 로딩 실패: {e}")

    def append(self, model_num, cluster_params, metrics, rank_stddev, rank_error_score):
        self.log.append({
            "timestamp": datetime.now().isoformat(),
            "model_num": model_num,
            "cluster_params": cluster_params,
            "metrics": metrics,
            "rank_stddev": rank_stddev,
            "rank_error_score": rank_error_score
        })
        self.save()

    def append_extended(
        self,
        model_num: str,
        cluster_params: dict,
        summary_metrics: dict,
        rank_error_score: float,
        rank_error_by_year: dict,
        rank_stddev_by_year: dict,
        mean_rank_stddev: float,
        n_clusters: int,
        cluster_R2: float,
        full_predict_R2: float,
        cluster_better_than_predict: bool
    ):
        self.log.append({
            "timestamp": datetime.now().isoformat(),
            "model_num": model_num,
            "n_clusters": n_clusters,
            "cluster_params": cluster_params,
            "summary_metrics": summary_metrics,
            "rank_error_score": rank_error_score,
            "rank_error_by_year": rank_error_by_year,
            "rank_stddev_by_year": rank_stddev_by_year,
            "mean_rank_stddev": mean_rank_stddev,
            "cluster_R2": cluster_R2,
            "full_predict_R2": full_predict_R2,
            "cluster_better_than_predict": cluster_better_than_predict
        })
        self.save()

    def save(self):
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2)

    def get_latest_log(self) -> dict:
        """
        로그 파일에서 가장 최근 로그(log[-1]) 가져오기.
        """
        if not self.log:
            return {}
        return self.log[-1]
    
    def append_xgb(
        self,
        model_num: str,
        model_type: str,
        trial_idx: int,
        window_size: int,
        r2_score: float,
        tuned_params: dict
        ):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_num": model_num,
            "model_type": model_type,
            "trial_idx": trial_idx,
            "window_size": window_size,
            "r2_score": r2_score,
            "params": tuned_params
        }
        self.log.append(entry)
        self.save()
