from pathlib import Path
from tunerengine import RandomTuner
from configmanager import ConfigManager
from tuningcyclerunner import run_ml_rfr_pipeline, get_latest_metrics
from tunerlogger import TunerLogger
from core_utiles.config_loader import RFR_CONFIG_PATH, RFR_METRICS_PATH

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

    def run(self):
        for trial in range(self.n_trials):
            print(f"\n[Trial {trial+1}/{self.n_trials}] 시작")

            # n_clusters를 먼저 샘플링
            sampled_nclusters = self.tuner.sample_params().get(
                "n_clusters",
                self.config.config["CLUSTER_CONFIG"]["n_clusters"]
            )
            self.config.set_n_clusters(sampled_nclusters)

            cluster_params_dict = {}

            # 클러스터 수에 따라 full + n개의 클러스터에 대해 각각 파라미터 샘플링
            for cluster_id in ["full"] + [str(i) for i in range(sampled_nclusters)]:
                sampled = self.tuner.sample_params()
                model_params = {
                    k: v for k, v in sampled.items() if k != "n_clusters"
                }
                self.config.update_cluster_params(cluster_id, model_params)
                cluster_params_dict[cluster_id] = model_params

            self.config.save()

            # 학습 및 평가
            run_ml_rfr_pipeline()
            summary_metrics = get_latest_metrics(self.metrics_path)

            # 로그 기록
            self.logger.append_cycle(sampled_nclusters, cluster_params_dict, summary_metrics)
