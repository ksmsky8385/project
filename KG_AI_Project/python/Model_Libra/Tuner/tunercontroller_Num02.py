import json
from datetime import datetime
from pathlib import Path

from tunerengine import RandomTuner
from configmanager import ConfigManager
from tunerlogger import TunerLogger
from tuningcyclerunner import run_modelcreator

class TunerController_Num02:
    def __init__(self, config_path: Path, log_dir: Path, trial_count: int, rating_cycle: int):
        self.config_path = config_path
        self.config = ConfigManager(config_path)
        self.model_num = self.config.get_model_num()
        self.model_type = self.config.get_model_type()
        self.model_name = self.config.get_model_name()

        self.tuner = RandomTuner(
            param_spec=self.config.get_tuning_params(),
            cluster_enabled=self.config.get_cluster_enabled()
        )

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = log_dir / f"{self.model_num}_Tuner_Log_{self.timestamp}.json"
        self.logger = TunerLogger(log_path)
        self.log_dir = log_dir
        self.n_trials = trial_count
        self.rating_cycle = rating_cycle

    def load_r2_from_log(self) -> float:
        log_file = Path(__file__).resolve().parent.parent / "_Logs" / f"{self.model_num}_{self.model_name}_v1.0_Log.json"
        if not log_file.exists():
            print(f"[경고] 로그 파일 없음: {log_file}")
            return -1

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                log_data = json.load(f)
            history = log_data.get("history", [])
            r2_values = [
                entry.get("full", {}).get("R2", -1)
                for entry in history
                if "full" in entry and entry.get("full", {}).get("R2", -1) >= 0
            ]
            return min(r2_values) if r2_values else -1
        except Exception as e:
            print(f"[R2 추출 오류] {e}")
            return -1

    def run(self):
        for trial in range(self.n_trials):
            print(f"\n[Trial {trial+1}/{self.n_trials}]")

            sampled = self.tuner.sample_params()
            self.config.update_with_sampled_params(sampled)

            run_modelcreator(self.config)

            r2_score = self.load_r2_from_log()
            print(f"[R2 추출] → {r2_score:.4f}")

            params = self.config.get_config().get("PARAMS", {}).get("full", {})
            window_size = params.get("window_size", -1)

            self.logger.append_xgb(
                model_num=self.model_num,
                model_type=self.model_type,
                trial_idx=trial + 1,
                window_size=window_size,
                r2_score=r2_score,
                tuned_params=self.config.get_config().get("PARAMS", {})
            )
