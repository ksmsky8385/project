import pandas as pd
import os

from ML_XGB.config import Config
from EstimationFuture.ModelLoader import ModelLoader
from core_utiles.config_loader import CSV_NUM09_PREFIX
from core_utiles.OracleDBConnection import OracleDBConnection
from core_utiles.OracleTableCreater import OTC

class SCRTableBuilder:
    def __init__(self, model_loader: ModelLoader):
        self.model = model_loader.load()

        self.db = OracleDBConnection()
        self.db.connect()
        self.conn = self.db.conn
        self.engine = self.db.engine

        self.window = Config.ROLLING_WINDOW
        self.prefix = CSV_NUM09_PREFIX
        self.default_columns = ["ID", "SNM", "STYP", "FND", "RGN", "USC"]
        self.latest_year = self._get_latest_year()
        self.predict_year = self.latest_year + 1

    def _get_latest_year(self) -> int:
        query = """
            SELECT MAX(TO_NUMBER(REGEXP_SUBSTR(table_name, '\\d{4}'))) AS MAX_YR
            FROM all_tables
            WHERE table_name LIKE 'NUM08_%' AND owner = 'LIBRA'
        """
        try:
            df = pd.read_sql(query, self.conn)
            return int(df.iloc[0]["MAX_YR"])
        except Exception as e:
            raise RuntimeError(f"[ERROR] Failed to retrieve latest year: {e}")

    def build_table(self):
        print(f"[Start] NUM09_Estimation generation - base year: {self.latest_year}, prediction year: {self.predict_year}")

        # Define input years based on window size (past years)
        input_years = [self.latest_year - i for i in reversed(range(self.window))]

        # Load base university info
        info_df = self._load_info(self.latest_year)

        # Load SCR_EST features for each year as SCR_EST_t-{i}
        scr_dfs = [self._load_scr_est(year, i) for i, year in enumerate(input_years)]
        feature_df = self._merge_scr_est_by_id(scr_dfs)

        # Merge features with university info
        table = pd.merge(info_df, feature_df, on="ID")

        # Predict future score using model
        feature_cols = [f"SCR_EST_t-{i}" for i in range(self.window)]
        input_df = table[feature_cols].copy()
        y_pred = self.model.predict(input_df)
        table[f"SCR_EST_{self.predict_year}"] = y_pred

        # Rename SCR_EST_t-{i} columns to SCR_EST_{year}
        rename_map = {
            f"SCR_EST_t-{i}": f"SCR_EST_{self.predict_year - (i + 1)}"
            for i in range(self.window)
        }
        table.rename(columns=rename_map, inplace=True)

        # Sort score columns by year ascending
        score_cols = sorted(rename_map.values(), key=lambda x: int(x.split("_")[-1]))
        final_cols = self.default_columns + score_cols + [f"SCR_EST_{self.predict_year}"]
        final_table = table[final_cols]

        # Sort ID descending
        final_table = final_table.sort_values(by="ID", ascending=True).reset_index(drop=True)

        # Save to CSV
        csv_path = os.path.join(self.prefix, "NUM09_가능성예측.csv")
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        final_table.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[CSV파일 생성완료] {csv_path}")

        # Create Oracle table
        cursor = self.conn.cursor()
        OTC(cursor, "NUM09_Estimation", final_table)
        print("[Oracle DB 테이블 생성 완료] NUM09_Estimation")

    def _load_scr_est(self, year: int, t_index: int) -> pd.DataFrame:
        query = f"SELECT ID, SCR_EST FROM LIBRA.NUM08_{year}"
        df = pd.read_sql(query, self.conn)
        return df.rename(columns={"SCR_EST": f"SCR_EST_t-{t_index}"})

    def _load_info(self, year: int) -> pd.DataFrame:
        query = f"""
            SELECT ID, SNM, STYP, FND, RGN, USC
            FROM LIBRA.NUM08_{year}
        """
        return pd.read_sql(query, self.conn)

    def _merge_scr_est_by_id(self, dfs: list[pd.DataFrame]) -> pd.DataFrame:
        merged = dfs[0]
        for df in dfs[1:]:
            merged = pd.merge(merged, df, on="ID")
        return merged
