import pandas as pd

class DataCleaner:
    def __init__(self):
        pass

    def clean_numeric(self, df: pd.DataFrame, target_cols: list) -> pd.DataFrame:
        df_cleaned = df.copy()
        for col in target_cols:
            try:
                cleaned = df_cleaned[col].astype(str).str.replace(",", "", regex=False).str.strip()
                df_cleaned[col] = pd.to_numeric(cleaned, errors="raise")
            except Exception as e:
                raise ValueError(f"[ERROR] 컬럼 '{col}' 변환 실패 → {e}")
        return df_cleaned