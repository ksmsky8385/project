import pandas as pd

class DataCleaner:
    def __init__(self):
        self.scaler = None  # 학습 후 저장용 (예측 시 재사용 가능)

    def clean_numeric(self, df: pd.DataFrame, target_cols: list) -> pd.DataFrame:
        df_cleaned = df.copy()
        for col in target_cols:
            try:
                cleaned = df_cleaned[col].astype(str).str.replace(",", "", regex=False).str.strip()
                df_cleaned[col] = pd.to_numeric(cleaned, errors="raise")
            except Exception as e:
                raise ValueError(f"[ERROR] 컬럼 '{col}' 변환 실패 → {e}")
        return df_cleaned

    def handle_missing(self, df, strategy, feature_cols=None):
        method = strategy.get("method", "drop")
        fill_value = strategy.get("fill_value", 0)
        zero_threshold_ratio = strategy.get("zero_threshold_ratio", None)

        df_cleaned = df.copy()

        # 0값 비율 기준으로 제거
        if zero_threshold_ratio is not None and feature_cols is not None:
            zero_counts = (df_cleaned[feature_cols] == 0).sum(axis=1)
            zero_ratio = zero_counts / len(feature_cols)
            drop_mask = zero_ratio > zero_threshold_ratio
            df_cleaned = df_cleaned[~drop_mask]

        # NaN 결측치 처리
        if method == "drop":
            df_cleaned = df_cleaned.dropna()
        elif method == "fill":
            df_cleaned = df_cleaned.fillna(fill_value)
        elif method == "mean":
            df_cleaned = df_cleaned.fillna(df_cleaned.mean(numeric_only=True))
        elif method == "median":
            df_cleaned = df_cleaned.fillna(df_cleaned.median(numeric_only=True))
        else:
            raise ValueError(f"[ERROR] 지원되지 않는 결측치 처리 방식: {method}")

        return df_cleaned

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