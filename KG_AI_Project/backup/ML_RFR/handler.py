from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.cluster import KMeans
import pandas as pd

class DataHandler:
    def __init__(self, scaler_config: dict):
        self.scaler_config = scaler_config
        self.scaler = self.get_scaler(scaler_config) if scaler_config.get("enabled", True) else None
        self.cluster_model = None  # 학습된 클러스터링 모델 (KMeans 등)
        
    @staticmethod
    def get_scaler(config: dict):
        scaler_type = config.get("type", "StandardScaler")
        scaler_params = config.get("params", {})

        if scaler_type == "StandardScaler":
            return StandardScaler(**scaler_params)
        elif scaler_type == "MinMaxScaler":
            return MinMaxScaler(**scaler_params)
        elif scaler_type == "RobustScaler":
            return RobustScaler(**scaler_params)
        else:
            raise ValueError(f"[ERROR] 지원되지 않는 스케일러 타입: {scaler_type}")
        
    # 스케일링
    def scale_features(self, df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
        df_scaled = df.copy()

        if self.scaler is None:
            print("[INFO] 스케일링 비활성화 → 원본 값 사용")
            return df_scaled

        try:
            scaled_values = self.scaler.fit_transform(df_scaled[feature_cols])
            df_scaled[feature_cols] = scaled_values
        except Exception as e:
            raise ValueError(f"[ERROR] 스케일링 실패 → {e}")

        return df_scaled


    # 클러스터링 수행: scaled features 기준 KMeans 클러스터링
    def assign_clusters(self, df: pd.DataFrame, feature_cols: list, config: dict) -> pd.DataFrame:
        df_clustered = df.copy()
        
        if not config.get("enabled", True):
            df_clustered["cluster_id"] = 0  # 모든 데이터를 하나의 클러스터로 처리
            self.cluster_model = None
            return df_clustered

        # 스케일링 처리
        if self.scaler is None:
            self.scaler = StandardScaler()
            scaled = self.scaler.fit_transform(df_clustered[feature_cols])
        else:
            scaled = self.scaler.transform(df_clustered[feature_cols])

        # 클러스터링 모델 적용
        self.cluster_model = KMeans(
            n_clusters=config["n_clusters"],
            random_state=config["random_state"]
        )

        labels = self.cluster_model.fit_predict(scaled)
        df_clustered["cluster_id"] = labels

        return df_clustered
