# DBHandling/TableMergerUploader.py
import os
import pandas as pd
from core_utiles.OracleDBConnection import OracleDBConnection
from core_utiles.OracleSchemaBuilder import OSB

class TableMergerUploader:
    def __init__(self, db: OracleDBConnection, years, common_cols, csv_prefix=None, table_prefix=None):
        self.db = db  # OracleDBConnection 객체
        self.conn = db.conn
        self.cursor = db.cursor
        self.years = years
        self.common_cols = [col.upper() for col in common_cols]
        self.csv_prefix = csv_prefix
        self.table_prefix = table_prefix

    def load_and_merge_tables(self, year):
        dfs = []

        for i in range(1, 6):
            table = f"NUM0{i}_{year}"
            try:
                df = pd.read_sql(f'SELECT * FROM "{table}"', self.conn)
                df.columns = [col.upper() for col in df.columns]
                df["YR"] = year
                dfs.append(df)
            except Exception as e:
                print(f"{table} 불러오기 실패: {e}")

        if not dfs:
            return None

        # ID 기준 병합
        df_base = dfs[0]
        for df_other in dfs[1:]:
            df_base = pd.merge(df_base, df_other, on="ID", how="outer", suffixes=('', '_dup'))

        # 공통컬럼 중복 제거
        for col in self.common_cols:
            dup_col = f"{col}_dup"
            if dup_col in df_base.columns:
                df_base.drop(columns=dup_col, inplace=True)

        df_base["ID"] = pd.to_numeric(df_base["ID"], errors="coerce")
        df_base.sort_values("ID", inplace=True)
        df_base.reset_index(drop=True, inplace=True)
        return df_base

    def upload_to_oracle(self, df, table_name):
        try:
            # OSB 함수 사용 → 컬럼별 데이터타입 추론
            col_defs = OSB(df)
            self.cursor.execute(f'DROP TABLE "{table_name}"')
            self.cursor.execute(f'CREATE TABLE "{table_name}" ({col_defs})')

            rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
            placeholders = ', '.join([f':{i+1}' for i in range(len(df.columns))])
            insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'

            self.cursor.executemany(insert_sql, rows)
            self.conn.commit()

            print(f"Oracle 저장 완료: {table_name} ({df.shape[0]}행 × {df.shape[1]}열)")
        except Exception as e:
            print(f"Oracle 저장 실패 ({table_name}): {e}")

    def save_csv(self, df, year):
        if not self.csv_prefix:
            return
        csv_path = f"{self.csv_prefix}_{year}.csv"
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"CSV 저장 완료 → {csv_path} ({df.shape[0]}행 × {df.shape[1]}열)")

    def process_all_years(self):
        for year in self.years:
            print(f"\n{year}년 병합 및 테이블 생성 시작...")
            df_merged = self.load_and_merge_tables(year)
            if df_merged is not None:
                if self.csv_prefix:
                    self.save_csv(df_merged, year)
                if self.table_prefix:
                    table_name = f"{self.table_prefix}_{year}"
                    self.upload_to_oracle(df_merged, table_name)
            else:
                print(f"{year}년: 병합할 테이블 없음")