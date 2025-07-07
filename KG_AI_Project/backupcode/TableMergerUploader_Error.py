import os
import pandas as pd

class TableMergerUploader:
    def __init__(self, conn, cursor, years, common_cols, csv_prefix=None, table_prefix=None):
        self.conn = conn
        self.cursor = cursor
        self.years = years
        self.common_cols = [col.upper() for col in common_cols]
        self.csv_prefix = csv_prefix  # 예: D:\mydata\TD_평가
        self.table_prefix = table_prefix  # 예: TD

    def load_and_merge_tables(self, year):
        dfs = []
        for i in range(1, 6):
            table = f"NUM0{i}_{year}"
            try:
                df = pd.read_sql(f"SELECT * FROM {table}", self.conn)
                df.columns = [col.upper() for col in df.columns]
                df["YR"] = year

                if i > 1:
                    df = df.drop(columns=[col for col in self.common_cols if col in df.columns])

                dfs.append(df)

            except Exception as e:
                print(f"❌ {table} 불러오기 실패: {e}")

        if dfs:
            return pd.concat(dfs, axis=1)
        else:
            return None

    def upload_to_oracle(self, df, table_name):
        try:
            columns = ', '.join([
                f'"{col}" CLOB' if df[col].dtype == 'object' else f'"{col}" FLOAT'
                for col in df.columns
            ])
            create_sql = f'CREATE TABLE "{table_name}" ({columns})'

            try:
                self.cursor.execute(f'DROP TABLE "{table_name}"')
            except:
                pass  # 테이블 없으면 무시

            self.cursor.execute(create_sql)

            rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
            placeholders = ', '.join([':' + str(i + 1) for i in range(len(df.columns))])
            insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'

            self.cursor.executemany(insert_sql, rows)
            self.conn.commit()

            print(f"📦 Oracle 저장 완료: {table_name} ({df.shape[0]}행 × {df.shape[1]}열)")
        except Exception as e:
            print(f"❌ Oracle 저장 실패: {table_name} → {e}")

    def save_csv(self, df, year):
        if self.csv_prefix:
            csv_path = f"{self.csv_prefix}_{year}.csv"
            folder = os.path.dirname(csv_path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            print(f"📁 CSV 저장 완료 → {csv_path} ({df.shape[0]}행 × {df.shape[1]}열)")

    def process_all_years(self):
        for year in self.years:
            print(f"\n🔄 {year}년 처리 중...")
            df_merged = self.load_and_merge_tables(year)
            if df_merged is not None:
                if self.csv_prefix:
                    self.save_csv(df_merged, year)

                if self.table_prefix:
                    td_table_name = f"{self.table_prefix}_{year}"
                    self.upload_to_oracle(df_merged, td_table_name)
            else:
                print(f"⚠️ {year}년: 병합할 테이블 없음")