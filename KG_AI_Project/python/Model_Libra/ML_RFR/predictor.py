import pandas as pd
from ML_RFR.cleaner import DataCleaner
from ML_RFR.utils.validator import validate_columns
from ML_RFR.utils.evaluator import evaluate_metrics

class ModelPredictor:
    def __init__(self, model, conn, input_cols):
        self.model = model
        self.conn = conn
        self.input_cols = input_cols

    def predict_by_table(self, table_name: str):
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=self.conn)

        if df.empty:
            raise ValueError(f"테이블 '{table_name}'에 데이터가 없습니다.")

        validate_columns(df, self.input_cols + ["SCR", "SNM"])

        cleaner = DataCleaner()
        df_cleaned = cleaner.clean_numeric(df, self.input_cols + ["SCR"])
        X = df_cleaned[self.input_cols]
        y_true = df_cleaned["SCR"].values
        y_pred = self.model.predict(X)
        snm_list = df_cleaned["SNM"].astype(str).values  # 대학명

        # 성능 지표 계산
        metrics = evaluate_metrics(y_true, y_pred)

        # 예측 결과 테이블 생성
        df_result = pd.DataFrame({
            "SNM": snm_list,
            "예측SCR": y_pred,
            "실제SCR": y_true
        })
        df_result["오차율"] = abs(df_result["예측SCR"] - df_result["실제SCR"]) / df_result["실제SCR"] * 100

        return df_result, metrics
