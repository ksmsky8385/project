import pandas as pd

class DataCleaner:
    def __init__(self):
        pass

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(subset=["SCR_EST"])  # 점수 없는 행 제외
        df = df.sort_values(["ID", "YR"]).reset_index(drop=True)
        return df
