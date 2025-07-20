import os
import json
import pandas as pd
from EstimationFlow.ModelLoader import ModelLoader
from ML_RFR.cleaner import DataCleaner
from core_utiles.config_loader import CSV_NUM08_PREFIX
from core_utiles.OracleTableCreater import OTC

class SCRTableBuilder:
    def __init__(self, conn, engine, year: str, source_table: str):
        self.conn = conn
        self.engine = engine
        self.year = year
        self.source_table = source_table
        self.output_table = f"NUM08_{year}"
        self.output_csv = f"{CSV_NUM08_PREFIX}_{year}.csv"

        self.model_bundle = ModelLoader().load()
        self.cleaner = DataCleaner()

        config_path = os.path.join(os.path.dirname(__file__), "..", "ML_RFR/config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.input_columns = config.get("INPUT_COLUMNS", [])
        self.cluster_cfg = config.get("CLUSTER_CONFIG", {})
        self.scaler_cfg = config.get("SCALER_CONFIG", {})

        os.makedirs(os.path.dirname(self.output_csv), exist_ok=True)

    def run(self) -> bool:
        try:
            print(f"[예측 시작] {self.source_table} → {self.output_table}")

            df_raw = pd.read_sql(f"SELECT * FROM {self.source_table}", con=self.conn)

            missing = [col for col in self.input_columns if col not in df_raw.columns]
            if missing:
                print(f"[입력 컬럼 누락] {missing}")
                return False

            df_clean = self.cleaner.clean_numeric(df_raw, self.input_columns)
            X = df_clean[self.input_columns]

            # 1. 스케일링
            if self.scaler_cfg.get("enabled", False) and "scaler" in self.model_bundle:
                print("[스케일러 적용] StandardScaler")
                scaler = self.model_bundle["scaler"]
                X = scaler.transform(X)

            # 2. 클러스터링 예측
            if self.cluster_cfg.get("enabled", False) and "cluster_model" in self.model_bundle:
                print("[클러스터링 적용] 군집 예측 및 RFR 분리 추론")
                cluster_model = self.model_bundle["cluster_model"]
                cluster_assignments = cluster_model.predict(X)

                predictions = []
                for cluster_id in range(self.cluster_cfg.get("n_clusters", 0)):
                    model = self.model_bundle["rfr_clusters"][cluster_id]
                    indices = (cluster_assignments == cluster_id)
                    if indices.sum() == 0:
                        print(f"[스킵] 클러스터 {cluster_id} ➜ 예측 대상 없음 — 생략")
                        continue
                    pred = model.predict(X[indices])
                    predictions.extend((idx, p) for idx, p in zip(df_raw.index[indices], pred))

                # 정렬된 결과 매핑
                predictions.sort()
                df_raw["SCR_EST"] = [p for _, p in predictions]

            else:
                print("[단일 모델 예측] Full RFR 사용")
                model = self.model_bundle["rfr_full"]
                df_raw["SCR_EST"] = model.predict(X)

            # 출력 구성
            final_cols = ["YR", "ID", "SNM", "STYP", "FND", "RGN", "USC", "SCR_EST"]
            df_out = df_raw[final_cols].sort_values(by="ID").reset_index(drop=True)

            # 테이블 + CSV 저장
            OTC(cursor=self.conn.cursor(), table_name=self.output_table, df=df_out)
            df_out.to_sql(name=self.output_table, con=self.engine, if_exists="append", index=False)
            df_out.to_csv(self.output_csv, index=False, encoding="utf-8-sig")

            print(f"[완료] {self.output_table} 테이블 및 CSV 저장 완료")
            return True

        except Exception as e:
            print(f"[실패] {self.year}년도 예측 실패 ➜ {e}")
            return False
