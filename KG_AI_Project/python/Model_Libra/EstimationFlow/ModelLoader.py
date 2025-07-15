import os
import json
import joblib
from core_utiles.config_loader import RFR_SAVE_PATH

class ModelLoader:
    def __init__(self, path=RFR_SAVE_PATH):
        self.path = path
        self.config_path = os.path.join(os.path.dirname(__file__), "..", "ML_RFR/config.json")
        self.models = {}

    def load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_filename(self, prefix: str, suffix: str, version: str, cluster_id: int = None):
        if cluster_id is not None:
            return f"{prefix}{cluster_id}_{version}{suffix}"
        return f"{prefix}{version}{suffix}"

    def load(self):
        config = self.load_config()

        scaler_cfg = config.get("SCALER_CONFIG", {})
        cluster_cfg = config.get("CLUSTER_CONFIG", {})
        rules = config.get("SAVE_NAME_RULES", {})
        version = rules.get("version", "v1.0")
        suffix = rules.get("suffix", ".pkl")

        # 1. 스케일러 로딩
        if scaler_cfg.get("enabled", False):
            scaler_filename = self.build_filename(rules["prefix_model_scaler"], suffix, version)
            scaler_path = os.path.join(self.path, scaler_filename)
            print(f"[로딩] 스케일러 ➜ {scaler_path}")
            self.models["scaler"] = joblib.load(scaler_path)

        # 2. 클러스터링 모델 로딩
        if cluster_cfg.get("enabled", False):
            cluster_filename = self.build_filename(rules["prefix_model_cluster"], suffix, version)
            cluster_path = os.path.join(self.path, cluster_filename)
            print(f"[로딩] 클러스터링 모델 ➜ {cluster_path}")
            self.models["cluster_model"] = joblib.load(cluster_path)

            n_clusters = cluster_cfg.get("n_clusters", 0)
            self.models["rfr_clusters"] = []

            for i in range(n_clusters):
                filename = self.build_filename(rules["prefix_rfr_cluster"], suffix, version, cluster_id=i)
                model_path = os.path.join(self.path, filename)
                print(f"[로딩] 클러스터 RFR({i}) ➜ {model_path}")
                self.models["rfr_clusters"].append(joblib.load(model_path))

        else:
            # 3. 단일 Full 모델 로딩
            filename = self.build_filename(rules["prefix_rfr_full"], suffix, version)
            model_path = os.path.join(self.path, filename)
            print(f"[로딩] Full RFR ➜ {model_path}")
            self.models["rfr_full"] = joblib.load(model_path)

        return self.models
