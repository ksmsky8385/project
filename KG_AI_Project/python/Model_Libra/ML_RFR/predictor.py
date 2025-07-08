import pandas as pd
from ML_RFR.cleaner import DataCleaner
from ML_RFR.utils.validator import validate_columns

class ModelPredictor:
    def __init__(self, model, conn, input_cols):
        self.model = model
        self.conn = conn
        self.input_cols = input_cols

    def predict_by_school(self, school_name: str, table_name: str):
        query = f"SELECT * FROM {table_name} WHERE TO_CHAR(SNM) = '{school_name}'"
        df = pd.read_sql(query, con=self.conn)

        if df.empty:
            raise ValueError(f"대학 '{school_name}'에 해당하는 데이터가 없습니다.")

        validate_columns(df, self.input_cols)

        cleaner = DataCleaner()
        df_cleaned = cleaner.clean_numeric(df, self.input_cols)
        X_new = df_cleaned[self.input_cols]

        score = self.model.predict(X_new)[0]
        return score, X_new