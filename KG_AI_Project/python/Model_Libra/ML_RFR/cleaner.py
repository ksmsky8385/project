from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd

class DataCleaner:
    def __init__(self):
        self.scaler = None       # 학습된 스케일러 객체
        self.cluster_model = None  # 학습된 클러스터링 모델 (KMeans 등)

    # 문자열 숫자 변환
    def clean_numeric(self, df: pd.DataFrame, target_cols: list) -> pd.DataFrame:
        df_cleaned = df.copy()
        for col in target_cols:
            try:
                cleaned = df_cleaned[col].astype(str).str.replace(",", "", regex=False).str.strip()
                df_cleaned[col] = pd.to_numeric(cleaned, errors="raise")
            except Exception as e:
                raise ValueError(f"[ERROR] 컬럼 '{col}' 변환 실패 → {e}")
        return df_cleaned

    def handle_missing(self, df, strategy):
        method = strategy.get("method", "drop")

        if method == "drop":
            df = df.dropna()
        elif method == "fill":
            fill_value = strategy.get("fill_value", 0)
            df = df.fillna(fill_value)
        elif method == "mean":
            df = df.fillna(df.mean(numeric_only=True))
        elif method == "median":
            df = df.fillna(df.median(numeric_only=True))
        else:
            raise ValueError(f"[ERROR] 지원되지 않는 결측치 처리 방식: {method}")

        return df

    def handle_outliers(self, df, strategy):
        method = strategy.get("method", "iqr")
        threshold = strategy.get("threshold", 1.5)
        df_out = df.copy()

        for col in df.select_dtypes(include=["float", "int"]).columns:
            if method == "zscore":
                z = (df[col] - df[col].mean()) / df[col].std()
                df_out = df_out[(abs(z) < threshold)]
            elif method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - threshold * IQR
                upper = Q3 + threshold * IQR
                df_out = df_out[(df[col] >= lower) & (df[col] <= upper)]
            elif method == "clip":
                df_out[col] = df[col].clip(lower=df[col].quantile(0.01), upper=df[col].quantile(0.99))
            else:
                raise ValueError(f"[ERROR] 지원되지 않는 이상치 처리 방식: {method}")

        return df_out
