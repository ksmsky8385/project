# DBHandling/FilteredScoreUploader.py
import os
import pandas as pd
from core_utiles.OracleDBConnection import OracleDBConnection
from core_utiles.OracleSchemaBuilder import OSB

class FilteredScoreUploader:
    def __init__(self, db: OracleDBConnection, years, input_abbr, csv_prefix=None, table_name=None):
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor
        self.years = years
        self.input_abbr = input_abbr
        self.csv_prefix = csv_prefix
        self.table_name = table_name
        self.meta_cols = ['YR', 'RK', 'SNM', 'SCR', 'ID', 'STYP', 'FND', 'RGN', 'USC']

    def run(self):
        yearwise_filtered = {}
        matched_cols_list = []

        for year in self.years:
            print(f"\n🔄 {year}년 데이터 처리 중...")

            try:
                df = pd.read_sql(f'SELECT * FROM "NUM07_{year}"', self.conn)
                df.columns = [col.upper() for col in df.columns]

                matched_abbr_cols = [
                    col for col in df.columns
                    if any(col == abbr or col.endswith(f"_{abbr}") for abbr in self.input_abbr)
                ]
                matched_cols_list.append(set(matched_abbr_cols))
                yearwise_filtered[year] = df

                print(f"{year}년 필터링된 컬럼 수: {len(matched_abbr_cols)}")

            except Exception as e:
                print(f"{year}년 처리 실패: {e}")

        if not yearwise_filtered:
            print("유효한 연도별 데이터 없음.")
            return

        # 공통 필터 컬럼 추출
        common_data_cols = sorted(set.intersection(*matched_cols_list))
        final_columns = self.meta_cols + common_data_cols
        print(f"\n모든 연도에 공통된 필터링 컬럼: {len(common_data_cols)}개")
        print(f"{common_data_cols}")

        # 연도별 정제
        filtered_dfs = []
        for year in self.years:
            df = yearwise_filtered[year].copy()

            for col in final_columns:
                if col not in df.columns:
                    df[col] = None

            df = df[final_columns]

            for col in self.meta_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()

            df = df.sort_values("SNM").reset_index(drop=True)
            filtered_dfs.append(df)
            print(f"{year}년 정제 완료 → {df.shape[0]}행")

        # 병합
        df_merged = pd.concat(filtered_dfs, ignore_index=True)
        df_merged["RK"] = pd.to_numeric(df_merged["RK"], errors="coerce")
        df_merged = df_merged.sort_values(by=["YR", "RK"]).reset_index(drop=True)

        # CSV 저장
        if self.csv_prefix:
            csv_path = f"{self.csv_prefix}.csv"
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            df_merged.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"\nCSV 저장 완료 → {csv_path} ({df_merged.shape[0]}행 × {df_merged.shape[1]}열)")

        # Oracle 저장
        if self.table_name:
            try:
                self.cursor.execute(f'DROP TABLE "{self.table_name}"')
            except:
                print(f"테이블 {self.table_name} 제거됨 또는 없음")

            col_defs = ', '.join([
                f'"{col}" CLOB' if df_merged[col].dtype == object else f'"{col}" FLOAT'
                for col in df_merged.columns
            ])
            self.cursor.execute(f'CREATE TABLE "{self.table_name}" ({col_defs})')

            rows = [tuple(row) for row in df_merged.itertuples(index=False, name=None)]
            placeholders = ', '.join([f':{i+1}' for i in range(len(df_merged.columns))])
            insert_sql = f'INSERT INTO "{self.table_name}" VALUES ({placeholders})'
            self.cursor.executemany(insert_sql, rows)
            self.conn.commit()

            print(f"Oracle 저장 완료 → {self.table_name} ({df_merged.shape[0]}행 × {df_merged.shape[1]}열)")