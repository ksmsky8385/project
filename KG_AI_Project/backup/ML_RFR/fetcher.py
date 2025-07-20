import pandas as pd

class DataFetcher:
    def __init__(self, conn):
        self.conn = conn

    def load_table(self, table_name: str) -> pd.DataFrame:
        query = f"SELECT * FROM {table_name}"
        return pd.read_sql(query, con=self.conn)