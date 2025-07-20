import pandas as pd

class DataFetcher:
    def __init__(self, conn):
        self.conn = conn

    def get_panel_data(self, years: list) -> pd.DataFrame:
        dfs = []
        for y in years:
            table = f"NUM08_{y}"
            query = f"SELECT ID, YR, SCR_EST, RK_EST FROM {table}"
            df = pd.read_sql(query, con=self.conn)
            df["YR"] = int(y)
            dfs.append(df)
        return pd.concat(dfs).sort_values(["ID", "YR"]).reset_index(drop=True)

    def load_table(self, table_name: str) -> pd.DataFrame:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=self.conn)
        return df