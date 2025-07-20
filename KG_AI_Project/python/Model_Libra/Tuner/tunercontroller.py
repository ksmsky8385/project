# Tuner_RFR/tunercontroller.py

from pathlib import Path
from tunerengine import RandomTuner
from configmanager import ConfigManager
from rankevaluator import (
    calculate_rank_error_by_years,
    calculate_rank_stddev_by_years,
    calculate_mean_stddev
)
from tuningcyclerunner import run_ml_rfr_pipeline, get_latest_metrics
from tunerlogger import TunerLogger
from tunerlogranker import TunerLogRanker 
from core_utiles.config_loader import (
    get_raw_years, RFR_CONFIG_PATH, RFR_METRICS_PATH,
    ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, ORACLE_CLIENT_PATH
)

import oracledb
import subprocess

class TunerController:
    def __init__(self, n_trials: int = 5):
        config_path = Path(RFR_CONFIG_PATH) / "config.json"
        metrics_path = Path(RFR_METRICS_PATH) / "metrics_log.json"
        searchspace_path = Path(__file__).parent / "searchspace.json"
        tuner_log_path = Path(__file__).parent / "tuner_log.json"

        self.config = ConfigManager(config_path, searchspace_path)
        self.tuner = RandomTuner(searchspace_path)
        self.logger = TunerLogger(tuner_log_path)
        self.metrics_path = metrics_path
        self.n_trials = n_trials

    def run(self, save_interval: int, top_k: int):
        for trial in range(self.n_trials):
            print(f"\n[Trial {trial+1}/{self.n_trials}] 시작")

            sampled_nclusters = self.tuner.sample_params().get(
                "n_clusters",
                self.config.config["CLUSTER_CONFIG"]["n_clusters"]
            )
            self.config.set_n_clusters(sampled_nclusters)

            cluster_params_dict = {}
            for cluster_id in ["full"] + [str(i) for i in range(sampled_nclusters)]:
                sampled = self.tuner.sample_params()
                model_params = {k: v for k, v in sampled.items() if k != "n_clusters"}
                self.config.update_cluster_params(cluster_id, model_params)
                cluster_params_dict[cluster_id] = model_params

            self.config.save()

            run_ml_rfr_pipeline()

            estimation_main = self.config.config_path.parent.parent / "EstimationFlow" / "__main__.py"
            subprocess.run(["python", str(estimation_main)], check=True)

            filtered_table = "FILTERED"
            years_to_evaluate = get_raw_years()

            oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_PATH)
            with oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN) as conn:
                error_by_year = calculate_rank_error_by_years(
                    filtered_table,
                    "NUM08",
                    years_to_evaluate,
                    conn
                )
                error_score = sum(error_by_year.values())

                stddev_by_year = calculate_rank_stddev_by_years(
                    filtered_table,
                    "NUM08",
                    years_to_evaluate,
                    conn
                )
                mean_stddev = calculate_mean_stddev(stddev_by_year)

            summary_metrics = get_latest_metrics(self.metrics_path)

            self.logger.append_cycle(
                sampled_nclusters,
                cluster_params_dict,
                summary_metrics,
                rank_error_score=error_score,
                rank_error_by_year=error_by_year,
                rank_stddev_by_year=stddev_by_year,
                mean_rank_stddev=mean_stddev
            )

            if (trial + 1) % save_interval == 0:
                print(f"[중간저장] Top {top_k} trial 기록 중 -> toprating.json 초기화")
                log_path = Path(__file__).parent / "tuner_log.json"
                output_path = Path(__file__).parent / "toprating.json"

                ranker = TunerLogRanker(log_path=log_path, output_path=output_path)
                ranker.rank_top_trials(top_k)