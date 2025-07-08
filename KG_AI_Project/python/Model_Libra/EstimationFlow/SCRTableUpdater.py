import os
import pandas as pd
from ML_RFR.config import INPUT_COLUMNS
from core_utiles.config_loader import CSV_NUM08_PREFIX
from core_utiles.OracleTableCreater import OTC

class SCRTableUpdater:
    def __init__(self, conn, engine, year: str, table_name: str):
        self.conn = conn
        self.engine = engine
        self.year = year
        self.table_name = table_name
        self.output_csv = f"{CSV_NUM08_PREFIX}_{year}.csv"
        os.makedirs(os.path.dirname(self.output_csv), exist_ok=True)

    def run(self) -> bool:
        try:
            print(f"[업데이트 시작] {self.table_name} -> 등수 + 인풋컬럼 병합")

            # 1. NUM08 테이블 로드
            query = f"SELECT * FROM {self.table_name}"
            df = pd.read_sql(query, con=self.conn)

            if "SCR_EST" not in df.columns:
                print(f"[오류] {self.table_name}에 SCR_EST 컬럼이 없습니다.")
                return False

            # 2. RK_EST 등수 컬럼 추가
            df["RK_EST"] = df["SCR_EST"].rank(method="min", ascending=False).astype(int)

            # 3. NUM06 테이블에서 INPUT_COLUMNS 가져오기
            source_table = f"LIBRA.NUM06_{self.year}"
            try:
                cols = ", ".join(["ID"] + INPUT_COLUMNS)
                query_input = f"SELECT {cols} FROM {source_table}"
                df_input = pd.read_sql(query_input, con=self.conn)
                df = pd.merge(df, df_input, on="ID", how="left")
            except Exception as merge_err:
                print(f"[경고] NUM06_{self.year} 테이블에서 입력 컬럼 병합 실패: {merge_err}")

            # 4. 컬럼 정렬: ID → 기타 → SCR_EST → RK_EST → 인풋컬럼
            other_cols = [c for c in df.columns if c not in ("SCR_EST", "RK_EST") + tuple(INPUT_COLUMNS)]
            cols_ordered = other_cols + ["SCR_EST", "RK_EST"] + [col for col in INPUT_COLUMNS if col in df.columns]
            df_out = df[cols_ordered]
            df_out = df_out.sort_values(by="ID").reset_index(drop=True)

            # 5. Oracle 테이블 재생성 + 삽입
            OTC(cursor=self.conn.cursor(), table_name=self.table_name, df=df_out)
            df_out.to_sql(name=self.table_name, con=self.engine, if_exists="append", index=False)

            # 6. CSV 저장
            df_out.to_csv(self.output_csv, index=False, encoding="utf-8-sig")

            print(f"[완료] 테이블 및 CSV 갱신 완료: {self.table_name}")
            return True

        except Exception as e:
            print(f"[실패] {self.year}년도 업데이트 실패 -> {e}")
            return False
