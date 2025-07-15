import os
import json
import oracledb

from ML_RFR.fetcher import DataFetcher
from ML_RFR.handler import DataHandler
from ML_RFR.cleaner import DataCleaner
from ML_RFR.trainer import ModelTrainer
from ML_RFR.predictor import ModelPredictor
from ML_RFR.utils.exporter import save_model

class RFRPipelineController:
    def __init__(self, conn, oracle_client_path, rfr_save_path, config_path=None):
        self.conn = conn
        self.oracle_client_path = oracle_client_path
        self.rfr_save_path = rfr_save_path
        if config_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "config.json")
        self.config = self.load_config(config_path)

    def load_config(self, path):
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
        raw_cluster_params = config.get("RFR_PARAMS_BY_CLUSTER", {})
        config["RFR_PARAMS_BY_CLUSTER"] = {str(k): v for k, v in raw_cluster_params.items()}

        return config

    def setup_oracle_client(self):
        try:
            oracledb.init_oracle_client(lib_dir=self.oracle_client_path)
            print(f"[Oracle Init] Instant Client 경로: {self.oracle_client_path}")
        except Exception as e:
            raise RuntimeError(f"[ERROR] Oracle 클라이언트 초기화 실패 → {e}")

    def run(self):
        print("[START] RFR 모델 훈련 및 예측 파이프라인")

        # Config 적용
        INPUT_COLUMNS = self.config["INPUT_COLUMNS"]
        TARGET_COLUMN = self.config["TARGET_COLUMN"]
        FILTERED_TABLE = self.config["FILTERED_TABLE"]
        MISSING_VALUE_STRATEGY = self.config["MISSING_VALUE_STRATEGY"]
        OUTLIER_STRATEGY = self.config["OUTLIER_STRATEGY"]
        SCALER_CONFIG = self.config["SCALER_CONFIG"]
        CLUSTER_CONFIG = self.config["CLUSTER_CONFIG"]
        RFR_PARAMS_BY_CLUSTER = self.config["RFR_PARAMS_BY_CLUSTER"]
        SAVE_NAME_RULES = self.config["SAVE_NAME_RULES"]

        # 1. 데이터 수집 및 전처리
        fetcher = DataFetcher(self.conn)
        df_raw = fetcher.load_table(FILTERED_TABLE)

        cleaner = DataCleaner()
        df_cleaned = cleaner.clean_numeric(df_raw, INPUT_COLUMNS + [TARGET_COLUMN])
        df_cleaned = cleaner.handle_missing(df_cleaned, MISSING_VALUE_STRATEGY, feature_cols=INPUT_COLUMNS)
        # df_cleaned = cleaner.handle_outliers(df_cleaned, OUTLIER_STRATEGY)

        handler = DataHandler(scaler_config=SCALER_CONFIG)
        df_scaled = handler.scale_features(df_cleaned, INPUT_COLUMNS)

        # 스케일러 저장
        scaler_filename = SAVE_NAME_RULES["prefix_model_scaler"] + SAVE_NAME_RULES["version"] + SAVE_NAME_RULES["suffix"]
        save_model(handler.scaler, os.path.join(self.rfr_save_path, scaler_filename))
        print(f"[저장 완료] 스케일러 → {scaler_filename}")

        df_clustered = handler.assign_clusters(df_scaled, INPUT_COLUMNS, CLUSTER_CONFIG)

        # 클러스터 모델 저장
        cluster_model_filename = SAVE_NAME_RULES["prefix_model_cluster"] + SAVE_NAME_RULES["version"] + SAVE_NAME_RULES["suffix"]
        save_model(handler.cluster_model, os.path.join(self.rfr_save_path, cluster_model_filename))
        print(f"[저장 완료] 클러스터 모델 → {cluster_model_filename}")

        # 2. 모델 트레이너 실행
        trainer = ModelTrainer(rfr_params_by_cluster=RFR_PARAMS_BY_CLUSTER, input_cols=INPUT_COLUMNS)

        # 전체 모델 학습 및 저장
        metrics_full = trainer.train(df_clustered[INPUT_COLUMNS], df_clustered[TARGET_COLUMN])
        print(f"[전체 모델] RMSE: {metrics_full['RMSE']:.4f} / MAE: {metrics_full['MAE']:.4f} / R2: {metrics_full['R2']:.4f}")

        model_full = trainer.models_by_cluster["full"]
        full_model_filename = SAVE_NAME_RULES["prefix_rfr_full"] + SAVE_NAME_RULES["version"] + SAVE_NAME_RULES["suffix"]
        save_model(model_full, os.path.join(self.rfr_save_path, full_model_filename))
        print(f"[전체 모델 저장] → {full_model_filename}")

        # 클러스터별 모델 학습 및 저장
        metrics_by_cluster = trainer.train_by_cluster(
            df=df_clustered,
            input_cols=INPUT_COLUMNS,
            target_col=TARGET_COLUMN,
            cluster_col="cluster_id"
        )

        print("\n[클러스터별 모델 성능]")
        for cid, score in metrics_by_cluster.items():
            print(f"Cluster {cid} → RMSE: {score['RMSE']:.4f} / MAE: {score['MAE']:.4f} / R2: {score['R2']:.4f}")

        for cid, model in trainer.models_by_cluster.items():
            filename = f"{SAVE_NAME_RULES['prefix_rfr_cluster']}{cid}_{SAVE_NAME_RULES['version']}{SAVE_NAME_RULES['suffix']}"
            save_model(model, os.path.join(self.rfr_save_path, filename))
            print(f"[클러스터 모델 저장] Cluster {cid} → {filename}")

        # 3. 예측 테스트 — 전체 모델 기준
        table_name = FILTERED_TABLE

        predictor_full_only = ModelPredictor(
            model=model_full,
            conn=self.conn,
            input_cols=INPUT_COLUMNS,
            scaler=handler.scaler,
            model_by_cluster=None,
            cluster_model=None
        )
        df_result_f, test_metrics_f = predictor_full_only.predict_by_table(table_name)

        print(f"\n[전체 모델 기반 예측테스트] 테이블명 : {table_name.split('.')[-1]}")
        print(f"→ RMSE: {test_metrics_f['RMSE']:.4f} / MAE: {test_metrics_f['MAE']:.4f} / R2: {test_metrics_f['R2']:.4f}")

        print("\n-> 전체 모델 예측 정확도 상위 Top5")
        for i, row in enumerate(df_result_f.sort_values(by="오차율").head(5).itertuples(), 1):
            print(f"{i}. {row.SNM} (예측: {row.예측SCR:.4f}, 실제: {row.실제SCR:.4f}, 오차율: {row.오차율:.4f}%)")

        print("\n-> 전체 모델 예측 정확도 하위 Top5")
        for i, row in enumerate(df_result_f.sort_values(by="오차율", ascending=False).head(5).itertuples(), 1):
            print(f"{i}. {row.SNM} (예측: {row.예측SCR:.4f}, 실제: {row.실제SCR:.4f}, 오차율: {row.오차율:.4f}%)")

        # 4. 클러스터 기반 예측
        predictor_cluster = ModelPredictor(
            model=model_full,
            model_by_cluster=trainer.models_by_cluster,
            cluster_model=handler.cluster_model,
            conn=self.conn,
            input_cols=INPUT_COLUMNS,
            scaler=handler.scaler
        )
        df_result_c, test_metrics_c = predictor_cluster.predict_by_cluster(table_name)

        print(f"\n[클러스터 기반 예측테스트] 테이블명 : {table_name.split('.')[-1]}")
        print(f"→ RMSE: {test_metrics_c['RMSE']:.4f} / MAE: {test_metrics_c['MAE']:.4f} / R2: {test_metrics_c['R2']:.4f}")

        print("\n-> 클러스터 기반 예측 정확도 상위 Top5")
        for i, row in enumerate(df_result_c.sort_values(by="오차율").head(5).itertuples(), 1):
            print(f"{i}. {row.SNM} (예측: {row.예측SCR:.4f}, 실제: {row.실제SCR:.4f}, 오차율: {row.오차율:.4f}%, 클러스터: {row.클러스터})")

        print("\n-> 클러스터 기반 예측 정확도 하위 Top5")
        for i, row in enumerate(df_result_c.sort_values(by="오차율", ascending=False).head(5).itertuples(), 1):
            print(f"{i}. {row.SNM} (예측: {row.예측SCR:.4f}, 실제: {row.실제SCR:.4f}, 오차율: {row.오차율:.4f}%, 클러스터: {row.클러스터})")

        return {
            "full_model": metrics_full,
            "full_predict": test_metrics_f,
            "cluster_test": test_metrics_c
        }
