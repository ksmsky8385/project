import pandas as pd

class DataMergerAndExporter:
    def __init__(self, conn, cursor, years, file_prefix, table_prefix):
        self.conn = conn
        self.cursor = cursor
        self.years = years
        self.file_prefix = file_prefix
        self.table_prefix = table_prefix

    def merge_and_save(self):
        for year in self.years:
            print(f"\n🔄 {year}년 처리 중...")

            try:
                df_num = pd.read_sql(f"SELECT * FROM NUM00_{year}", self.conn)
                df_td = pd.read_sql(f"SELECT * FROM NUM06_{year}", self.conn)
            except Exception as e:
                print(f"❌ {year}년 데이터 로딩 실패: {e}")
                continue

            df_num.columns = [col.upper() for col in df_num.columns]
            df_td.columns = [col.upper() for col in df_td.columns]

            df_num["SNM"] = df_num["SNM"].astype(str).str.strip().str.upper()
            df_td["SNM"] = df_td["SNM"].astype(str).str.strip().str.upper()

            td_filtered = df_td[df_td["SNM"].isin(df_num["SNM"])].copy()

            unmatched_snms = df_num[~df_num["SNM"].isin(df_td["SNM"])]["SNM"].tolist()
            if unmatched_snms:
                print(f"⚠️ [경고] {year}년: NUM00에 있는 SNM 중 {len(unmatched_snms)}개가 TD에 없음!")
                print(f"   누락된 SNM 목록 ➜ {unmatched_snms}")

            td_filtered = td_filtered.set_index("SNM").reindex(df_num["SNM"].values).reset_index()

            overlap_cols = [col for col in td_filtered.columns if col in df_num.columns and col != "SNM"]
            td_filtered = td_filtered.drop(columns=overlap_cols)

            df_merge = pd.concat([df_num.reset_index(drop=True), td_filtered.drop(columns="SNM")], axis=1)

            # 💾 CSV 저장
            csv_path = f"{self.file_prefix}_{year}.csv"
            df_merge.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"📁 저장 완료: {csv_path} ({df_merge.shape[0]}행 × {df_merge.shape[1]}열)")

            # 🧱 Oracle 테이블 생성 및 업로드
            self.upload_to_oracle(df_merge, year)

    def upload_to_oracle(self, df, year):
        table_name = f"{self.table_prefix}_{year}"
        try:
            # 컬럼 정의
            columns = ', '.join([
                f'"{col}" CLOB' if df[col].dtype == 'object' else f'"{col}" FLOAT'
                for col in df.columns
            ])
            try:
                self.cursor.execute(f'DROP TABLE "{table_name}"')
            except Exception as e:
                if "ORA-00942" in str(e):
                    print(f"ℹ️ {table_name} 테이블이 존재하지 않아 DROP 생략")
                else:
                    raise
            self.cursor.execute(f'CREATE TABLE "{table_name}" ({columns})')

            rows = [tuple(r) for r in df.itertuples(index=False, name=None)]
            placeholders = ', '.join([f":{i+1}" for i in range(len(df.columns))])
            insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'
            self.cursor.executemany(insert_sql, rows)
            self.conn.commit()

            print(f"📦 DB 업로드 완료 → {table_name} ({df.shape[0]}행 × {df.shape[1]}열)")

        except Exception as e:
            print(f"❌ Oracle 저장 실패: {table_name} → {e}")