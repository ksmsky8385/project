import os
import pandas as pd
from core_utiles.config_loader import get_raw_years
from core_utiles.OracleTableCreater import OTC
from ModelCreator.Cleaner import DataCleaner
from Predictor.PickleLoader import PickleLoader

class TableBuilder:
    def __init__(self, config: dict, conn, engine):
        self.config = config
        self.conn = conn
        self.engine = engine
        self.models = PickleLoader(config=self.config).load()

        cleaner_enabled = (
            self.config.get("MISSING_VALUE_STRATEGY", {}).get("enable", False) or
            self.config.get("OUTLIER_STRATEGY", {}).get("enable", False)
        )
        self.cleaner = DataCleaner(self.config) if cleaner_enabled else None

        self.import_cfg = self.config["PREDICTOR_CONFIG"]["IMPORT_CONFIG"]
        self.export_cfg = self.config["PREDICTOR_CONFIG"]["EXPORT_CONFIG"]

    def _get_targets(self):
        if self.import_cfg["IMPORT_TYPE"] == "LIST":
            list_name = self.import_cfg["LIST_NAME"]
            if list_name == "YR":
                return [str(y) for y in get_raw_years()]
            else:
                raise ValueError(f"[ERROR] 지원되지 않는 LIST_NAME: {list_name}")
        elif self.import_cfg["IMPORT_TYPE"] == "SINGLE":
            return [""]
        else:
            raise ValueError(f"[ERROR] 지원되지 않는 IMPORT_TYPE: {self.import_cfg['IMPORT_TYPE']}")

    def _load_data(self, key: str) -> pd.DataFrame:
        table_type = self.import_cfg["TABLE_TYPE"]

        if table_type == "DB":
            prefix = self.import_cfg["DB_CONFIG"]["TABLE_PREFIX"]
            table_name = f"{prefix}_{key}" if key else prefix
            query = f"SELECT * FROM LIBRA.{table_name}"
            return pd.read_sql(query, con=self.conn)

        elif table_type == "CSV":
            prefix = self.import_cfg["CSV_CONFIG"]["FILE_PREFIX"]
            path = self.import_cfg["CSV_CONFIG"]["FILE_PATH"]
            filename = f"{prefix}_{key}.csv" if key else f"{prefix}.csv"
            return pd.read_csv(os.path.join(path, filename))

        else:
            raise ValueError(f"[ERROR] 지원되지 않는 TABLE_TYPE: {table_type}")

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        input_cols = self.config["INPUT_COLUMNS"]
        missing_cfg = self.config.get("MISSING_VALUE_STRATEGY", {})
        zero_threshold = missing_cfg.get("zero_threshold_ratio", 0.5)
        nullify_by_row = missing_cfg.get("nullify_score_by_row", False)

        df_clean = df.copy()
        if self.cleaner:
            df_clean = self.cleaner.clean_numeric(df_clean, input_cols)
            df_clean = self.cleaner.handle_missing(df_clean, input_cols)
            df_clean = self.cleaner.handle_outliers(df_clean, input_cols)

        df_clean = df_clean.reset_index(drop=True)
        X = df_clean[input_cols]

        if self.config["SCALER_CONFIG"].get("enabled", False) and "scaler" in self.models:
            scaler = self.models["scaler"]
            X = scaler.transform(X)

        if self.config["CLUSTER_CONFIG"].get("enabled", False) and "cluster_model" in self.models:
            cluster_model = self.models["cluster_model"]
            cluster_assignments = cluster_model.predict(X)

            df_clean["SCR_EST"] = None
            for cluster_id in range(len(self.models["rfr_clusters"])):
                model = self.models["rfr_clusters"][cluster_id]
                indices = (cluster_assignments == cluster_id)
                if indices.sum() == 0:
                    continue
                preds = model.predict(X[indices])
                df_clean.loc[indices, "SCR_EST"] = preds
        else:
            model = self.models["rfr_full"]
            df_clean["SCR_EST"] = model.predict(X)

        if nullify_by_row:
            df_clean["__zero_ratio__"] = df_clean[input_cols].apply(lambda row: (row == 0).mean(), axis=1)
            to_nullify = df_clean[df_clean["__zero_ratio__"] > zero_threshold]

            for idx, row in to_nullify.iterrows():
                row_snm = row.get("SNM", f"index_{idx}")
                print(f"[INFO] '{row_snm}' 예측 제외 (0값 비율: {row['__zero_ratio__']:.2f})")
                df_clean.at[idx, "SCR_EST"] = None

            df_clean = df_clean.drop(columns=["__zero_ratio__"])

        return df_clean

    def export(self, df: pd.DataFrame, key: str):
        drop_enabled = self.export_cfg.get("DROP_ENABLE", False)
        remain_cols = self.export_cfg.get("REMAIN_COLS", [])
        db_prefix = self.export_cfg["DB_CONFIG"]["TABLE_PREFIX"]
        csv_prefix = self.export_cfg["CSV_CONFIG"]["FILE_PREFIX"]
        csv_path = self.export_cfg["CSV_CONFIG"]["FILE_PATH"]

        table_name = f"{db_prefix}_{key}" if key else db_prefix
        file_name = f"{csv_prefix}_{key}.csv" if key else f"{csv_prefix}.csv"
        file_path = os.path.join(csv_path, file_name)

        if drop_enabled:
            df = df[remain_cols + ["SCR_EST"]]
        else:
            if "SCR_EST" not in df.columns:
                df["SCR_EST"] = None

        df_out = df.sort_values(by="ID").reset_index(drop=True)

        OTC(cursor=self.conn.cursor(), table_name=table_name, df=df_out)
        df_out.to_sql(name=table_name, con=self.engine, if_exists="append", index=False)
        df_out.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"[저장 완료] {table_name} / {file_name}")

    def run(self):
        for key in self._get_targets():
            try:
                df = self._load_data(key)
                df_pred = self.predict(df)
                self.export(df_pred, key)
                print(f"[완료] {key or '단일'} 예측 및 저장 완료")
            except Exception as e:
                print(f"[오류] {key or '단일'} 처리 실패 ➜ {e}")
