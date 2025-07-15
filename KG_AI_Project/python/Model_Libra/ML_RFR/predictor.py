import pandas as pd
import numpy as np
from joblib import load
from ML_RFR.cleaner import DataCleaner
from ML_RFR.utils.validator import validate_columns
from ML_RFR.utils.evaluator import evaluate_metrics

class ModelPredictor:
    def __init__(self, model=None, conn=None, input_cols=None,
                scaler=None, scaler_path=None,
                model_by_cluster=None, cluster_model=None):
        self.model = model
        self.model_by_cluster = model_by_cluster  # 클러스터별 모델 dict
        self.cluster_model = cluster_model  # KMeans 등 클러스터 모델
        self.conn = conn
        self.input_cols = input_cols

        # 스케일러 지정 방식 우선순위: 직접 전달 > 경로 로딩 > 없음
        if scaler is not None:
            self.scaler = scaler
        elif scaler_path is not None:
            try:
                self.scaler = load(scaler_path)
            except Exception as e:
                raise ValueError(f"[ERROR] 스케일러 로드 실패 → {e}")
        else:
            self.scaler = None  # 스케일러 없이도 동작 가능

    def predict_by_table(self, table_name: str):
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=self.conn)

        if df.empty:
            raise ValueError(f"[ERROR] 테이블 '{table_name}'에 데이터가 없습니다.")

        validate_columns(df, self.input_cols + ["SCR", "SNM"])

        cleaner = DataCleaner()
        df_cleaned = cleaner.clean_numeric(df, self.input_cols + ["SCR"])

        X_raw = df_cleaned[self.input_cols]

        # 스케일링 적용
        if self.scaler:
            X_scaled = self.scaler.transform(X_raw)
        else:
            X_scaled = X_raw

        y_true = df_cleaned["SCR"].values
        y_pred = self.model.predict(X_scaled)
        snm_list = df_cleaned["SNM"].astype(str).values

        metrics = evaluate_metrics(y_true, y_pred)

        df_result = pd.DataFrame({
            "SNM": snm_list,
            "예측SCR": y_pred,
            "실제SCR": y_true
        })
        df_result["오차율"] = abs(df_result["예측SCR"] - df_result["실제SCR"]) / df_result["실제SCR"] * 100

        return df_result, metrics

    def predict_by_cluster(self, table_name: str):
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=self.conn)

        if df.empty:
            raise ValueError(f"[ERROR] 테이블 '{table_name}'에 데이터가 없습니다.")

        validate_columns(df, self.input_cols + ["SCR", "SNM"])

        cleaner = DataCleaner()
        df_cleaned = cleaner.clean_numeric(df, self.input_cols + ["SCR"])

        X_raw = df_cleaned[self.input_cols]
        y_true = df_cleaned["SCR"].values
        snm_list = df_cleaned["SNM"].astype(str).values

        # 스케일링
        if self.scaler:
            X_scaled = self.scaler.transform(X_raw)
        else:
            X_scaled = X_raw

        # 클러스터 예측
        if self.cluster_model is None or self.model_by_cluster is None:
            # 클러스터링이 꺼진 경우, 전체 모델로 예측 수행
            print("[INFO] 클러스터 모델 없음 → 전체 모델 기반 예측으로 전환")
            y_pred = self.model.predict(X_scaled)
            df_result = pd.DataFrame({
                "SNM": snm_list,
                "예측SCR": y_pred,
                "실제SCR": y_true,
                "클러스터": 0
            })
        else:
            # 클러스터 기반 예측 수행
            cluster_ids = self.cluster_model.predict(X_scaled)

            y_pred = np.zeros(len(X_scaled))
            for cluster_id in np.unique(cluster_ids):
                indices = np.where(cluster_ids == cluster_id)[0]
                X_sub = X_scaled[indices]
                model = self.model_by_cluster.get(cluster_id)
                if model is None:
                    raise ValueError(f"[ERROR] 클러스터 {cluster_id}에 해당하는 모델이 없습니다.")
                y_pred_sub = model.predict(X_sub)
                y_pred[indices] = y_pred_sub

            df_result = pd.DataFrame({
                "SNM": snm_list,
                "예측SCR": y_pred,
                "실제SCR": y_true,
                "클러스터": cluster_ids
            })

        df_result["오차율"] = abs(df_result["예측SCR"] - df_result["실제SCR"]) / df_result["실제SCR"] * 100
        metrics = evaluate_metrics(y_true, y_pred)

        return df_result, metrics
