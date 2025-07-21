import json
from datetime import datetime
from pathlib import Path

from tunerengine import RandomTuner
from configmanager import ConfigManager
from tunerlogger import TunerLogger
from tuningcyclerunner import run_modelcreator, run_predictor
from rankevaluator import (
    calculate_rank_stddev_by_years,
    calculate_rank_error_by_years,
    calculate_mean_stddev
)
from tunerlogranker import TunerLogRanker
from core_utiles.OracleDBConnection import OracleDBConnection

def load_latest_metrics_from_log(log_dir: Path, model_num: str, model_name: str, version: str = "v1.0") -> dict:
    log_filename = f"{model_num}_{model_name}_{version}_Log.json"
    path = log_dir / log_filename
    if not path.exists():
        print(f"[경고] 로그 파일 없음: {path}")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and "history" in data:
            for entry in data["history"]:
                if entry.get("log_num") == 1:
                    return entry
        return {}
    except Exception as e:
        print(f"[경고] 로그 로딩 오류: {e}")
        return {}

class TunerController_Num01:
    def __init__(self, config_path: Path, log_dir: Path, trial_count: int, rating_cycle: int):
        self.config_path = config_path
        self.config = ConfigManager(config_path)
        self.model_num = self.config.get_model_num()
        self.model_type = self.config.get_model_type()
        self.model_name = self.config.get_model_name()
        self.tuner = RandomTuner(self.config.get_tuning_params())

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 공유 타임스탬프
        log_path = log_dir / f"{self.model_num}_Tuner_Log_{self.timestamp}.json"
        self.logger = TunerLogger(log_path)
        self.ranker = TunerLogRanker(log_dir, self.model_num, self.timestamp)

        self.log_dir = log_dir
        self.n_trials = trial_count
        self.rating_cycle = rating_cycle

    def run(self):
        for trial in range(self.n_trials):
            print(f"\nTrial {trial + 1} of {self.n_trials}")

            sampled = self.tuner.sample_params()
            self.config.update_with_sampled_params(sampled)

            run_modelcreator(self.config)
            run_predictor(self.config)

            try:
                oracle = OracleDBConnection()
                oracle.connect()
                conn = oracle.conn
                years = list(range(2014, 2025))
                stddev_by_year = calculate_rank_stddev_by_years(years, conn)
                error_by_year = calculate_rank_error_by_years(years, conn)
                mean_std = calculate_mean_stddev(stddev_by_year)
                total_error = sum(v for v in error_by_year.values() if v >= 0)
                oracle.close()
            except Exception as e:
                print(f"[오라클 평가 오류] {e}")
                stddev_by_year, error_by_year = {}, {}
                mean_std = -1
                total_error = -1

            metrics_log_dir = Path(__file__).resolve().parent.parent / "_Logs"
            log_data = load_latest_metrics_from_log(metrics_log_dir, self.model_num, self.model_name, version="v1.0")

            cluster_R2 = log_data.get("clustered", {}).get("R2", -1)
            full_predict_R2 = log_data.get("full", {}).get("R2", -1)
            better = cluster_R2 > full_predict_R2
            summary_metrics = {
                "full_predict": log_data.get("full", {}),
                "cluster_test": log_data.get("clustered", {})
            }

            print("[디버그] summary_metrics =", json.dumps(summary_metrics, indent=2))
            print("[디버그] cluster_R2 =", cluster_R2)
            print("[디버그] full_predict_R2 =", full_predict_R2)

            self.logger.append_extended(
                model_num=self.model_num,
                cluster_params=self.config.get_config().get("PARAMS", {}),
                summary_metrics=summary_metrics,
                rank_error_score=total_error,
                rank_error_by_year=error_by_year,
                rank_stddev_by_year=stddev_by_year,
                mean_rank_stddev=mean_std,
                n_clusters=sampled.get("n_clusters", -1),
                cluster_R2=cluster_R2,
                full_predict_R2=full_predict_R2,
                cluster_better_than_predict=better
            )

            if (trial + 1) % self.rating_cycle == 0:
                logs = self.ranker.load_trials()
                top_trials = self.ranker.rank_top_trials(top_k=5)
                self.ranker.save_rating_log(top_trials, cycle_idx=trial + 1)
