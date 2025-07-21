import json
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_model_num(self):
        return self.config.get("MODEL_NUM", "")

    def get_model_type(self):
        return self.config.get("MODEL_TYPE", "")
    
    def get_model_name(self):
        return self.config.get("MODEL_NAME", "")

    def get_tuning_params(self):
        return self.config.get("TUNING_PARAMS", {})

    def get_cluster_count(self):
        return self.config.get("CLUSTER_CONFIG", {}).get("params", {}).get("KMeans", {}).get("n_clusters", 1)

    def get_cluster_enabled(self) -> bool:
        return self.config.get("CLUSTER_CONFIG", {}).get("enabled", False)

    def update_with_sampled_params(self, sampled: dict):
        cluster_enabled = self.get_cluster_enabled()

        if cluster_enabled:
            # 클러스터가 켜져 있을 경우: full + 각 클러스터별 파라미터 포함
            n_clusters = sampled.get("n_clusters", 3)
            self.config["CLUSTER_CONFIG"]["params"]["KMeans"]["n_clusters"] = n_clusters
            self.config["PARAMS"] = {"n_clusters": n_clusters, "full": sampled.get("full", {})}

            for i in range(n_clusters):
                key = str(i)
                self.config["PARAMS"][key] = sampled.get(key, {})

        else:
            # 클러스터가 꺼져 있을 경우: 단일 full 파라미터만 반영
            self.config["PARAMS"] = {
                "full": sampled
            }

        # window_size를 WINDOW_CONFIG에도 반영
        window_size = sampled.get("window_size", sampled.get("full", {}).get("window_size", 3))
        if "WINDOW_CONFIG" not in self.config:
            self.config["WINDOW_CONFIG"] = {}
        self.config["WINDOW_CONFIG"]["window_size"] = window_size

        self.dump()

    def dump(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def get_config(self):
        return self.config
