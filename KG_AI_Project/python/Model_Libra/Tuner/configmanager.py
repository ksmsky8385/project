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

    def update_with_sampled_params(self, sampled: dict):
        # Update cluster count
        n_clusters = sampled.get("n_clusters", 3)
        if "CLUSTER_CONFIG" not in self.config:
            self.config["CLUSTER_CONFIG"] = {"params": {"KMeans": {}}}
        self.config["CLUSTER_CONFIG"]["params"]["KMeans"]["n_clusters"] = n_clusters

        # Build PARAMS dictionary from sampled structure:
        # sampled = {
        #     "n_clusters": 3,
        #     "full": { ... },
        #     "0": { ... },
        #     "1": { ... },
        #     "2": { ... }
        # }

        self.config["PARAMS"] = {"n_clusters": n_clusters}

        # Full model parameters
        self.config["PARAMS"]["full"] = sampled.get("full", {})

        # Cluster-specific model parameters
        for i in range(n_clusters):
            key = str(i)
            self.config["PARAMS"][key] = sampled.get(key, {})

        self.dump()

    def dump(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def get_config(self):
        return self.config
