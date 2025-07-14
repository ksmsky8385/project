import json
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: Path, searchspace_path: Path):
        self.config_path = config_path
        self.searchspace_path = searchspace_path
        self.config = self._load_config()
        self.searchspace = self._load_searchspace()

    def _load_config(self) -> dict:
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_searchspace(self) -> dict:
        with open(self.searchspace_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_cluster_params(self, cluster_id: str, params: dict):
        if "RFR_PARAMS_BY_CLUSTER" not in self.config:
            self.config["RFR_PARAMS_BY_CLUSTER"] = {}
        self.config["RFR_PARAMS_BY_CLUSTER"][cluster_id] = params

    def set_n_clusters(self, n_clusters: int):
        self.config["CLUSTER_CONFIG"]["n_clusters"] = n_clusters

    def save(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def get_config(self) -> dict:
        return self.config
