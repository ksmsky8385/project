import os
import pandas as pd
from EstimationFlow.ModelLoader import ModelLoader
from ML_RFR.cleaner import DataCleaner
from ML_RFR.config import INPUT_COLUMNS
from core_utiles.config_loader import CSV_NUM08_PREFIX
from core_utiles.OracleTableCreater import OTC

class SCRTableBuilder:
    def __init__(self, conn, engine, year: str, source_table: str):
        self.conn = conn          # oracledb connection
        self.engine = engine      # SQLAlchemy engine
        self.year = year
        self.source_table = source_table
        self.output_table = f"NUM08_{year}"
        self.output_csv = f"{CSV_NUM08_PREFIX}_{year}.csv"

        self.model = ModelLoader().load()
        self.cleaner = DataCleaner()

        os.makedirs(os.path.dirname(self.output_csv), exist_ok=True)

    def run(self) -> bool:
        try:
            print(f"[예측 시작] {self.source_table} → {self.output_table}")

            query = f"SELECT * FROM {self.source_table}"
            df = pd.read_sql(query, con=self.conn)

            print(f"원본 테이블: {self.source_table}")

            missing = [col for col in INPUT_COLUMNS if col not in df.columns]
            print(f"입력 컬럼 누락 개수: {len(missing)}")
            if missing:
                print(f"[DEBUG] 누락된 컬럼명: {missing}")

            print(f"예측 대상 행 수: {len(df)}")

            df_clean = self.cleaner.clean_numeric(df, INPUT_COLUMNS)
            predictions = self.model.predict(df_clean[INPUT_COLUMNS])
            df["SCR_EST"] = predictions

            final_cols = ["YR", "ID", "SNM", "STYP", "FND", "RGN", "USC", "SCR_EST"]
            df_out = df[final_cols]
            df_out = df_out.sort_values(by="ID").reset_index(drop=True)

            # 테이블 생성 (Oracle 전용 커서 사용)
            OTC(cursor=self.conn.cursor(), table_name=self.output_table, df=df_out)

            # 데이터 삽입 (SQLAlchemy 엔진 사용)
            df_out.to_sql(name=self.output_table, con=self.engine, if_exists="append", index=False)

            # CSV 저장
            df_out.to_csv(self.output_csv, index=False, encoding="utf-8-sig")

            print(f"[완료] 테이블 저장: {self.output_table}")
            print(f"[완료] 파일 저장: {self.output_csv}")
            return True

        except Exception as e:
            print(f"[실패] {self.year}년도 예측 실패 ➜ {e}")
            return False