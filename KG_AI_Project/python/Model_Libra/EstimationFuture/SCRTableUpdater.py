import pandas as pd
import os

from ML_XGB.config import Config
from EstimationFuture.ModelLoader import ModelLoader
from core_utiles.config_loader import CSV_NUM09_PREFIX
from core_utiles.OracleDBConnection import OracleDBConnection
from core_utiles.OracleTableCreater import OTC

class SCRTableUpdater:
    def __init__(self, model_loader: ModelLoader):
        self.model = model_loader.load()
        self.window = Config.ROLLING_WINDOW
        self.prefix = CSV_NUM09_PREFIX

        self.db = OracleDBConnection()
        self.db.connect()
        self.conn = self.db.conn

        # CSV 경로 구성
        self.csv_path = os.path.join(self.prefix, "NUM09_가능성예측.csv")
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Table file not found: {self.csv_path}")

    def update_table(self):
        print(f"[Updater] Loading table: {self.csv_path}")
        df = pd.read_csv(self.csv_path, encoding="utf-8-sig")

        # 최신 점수 컬럼 연도 추출
        score_cols = [col for col in df.columns if col.startswith("SCR_EST_20")]
        latest_year = max([int(col.split("_")[-1]) for col in score_cols])
        predict_year = latest_year + 1

        # 윈도우 기반 입력 컬럼 선택
        input_years = [predict_year - (self.window - i) for i in range(self.window)]
        input_cols = [f"SCR_EST_{yr}" for yr in input_years]

        # 컬럼 존재 여부 확인
        for col in input_cols:
            if col not in df.columns:
                raise ValueError(f"Missing input column for model: {col}")

        # 컬럼명 매핑: SCR_EST_{yr} → SCR_EST_t-{i}
        rename_map = {
            col: f"SCR_EST_t-{self.window - (i + 1)}"
            for i, col in enumerate(input_cols)
        }
        model_input = df[input_cols].copy().rename(columns=rename_map)

        # 예측 수행
        feature_order = [f"SCR_EST_t-{i}" for i in range(self.window)]
        model_input = model_input[feature_order]
        y_pred = self.model.predict(model_input)

        # 결과 저장
        df[f"SCR_EST_{predict_year}"] = y_pred

        # 컬럼 정렬: 점수 컬럼 오름차순으로 재정렬
        updated_score_cols = [col for col in df.columns if col.startswith("SCR_EST_20")]
        sorted_scores = sorted(updated_score_cols, key=lambda x: int(x.split("_")[-1]))
        final_cols = self._get_default_columns(df) + sorted_scores
        final_df = df[final_cols].sort_values("ID").reset_index(drop=True)

        # CSV 저장
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        final_df.to_csv(self.csv_path, index=False, encoding="utf-8-sig")
        print(f"[Updater] CSV updated: {self.csv_path}")

        # Oracle 테이블 갱신
        cursor = self.conn.cursor()
        OTC(cursor, "NUM09_Estimation", final_df)
        print(f"[Updater] Oracle table updated: LIBRA.NUM09_Estimation")

    def _get_default_columns(self, df: pd.DataFrame) -> list:
        default_candidates = ["ID", "SNM", "STYP", "FND", "RGN", "USC"]
        return [col for col in default_candidates if col in df.columns]
