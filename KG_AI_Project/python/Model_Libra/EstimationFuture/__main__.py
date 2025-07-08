import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_utiles.config_loader import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN
from core_utiles.OracleDBConnection import OracleDBConnection
from EstimationFlow.SCRTableBuilder import SCRTableBuilder
from EstimationFlow.SCRTableUpdater import SCRTableUpdater
import pandas as pd

owner = ORACLE_USER.upper()

print("[EstimationFlow] 예측 테이블 생성 시작")

# 오라클 DB 연결 객체 초기화 및 접속
db = OracleDBConnection()
db.connect()

# 연도 자동 추출
def get_available_years(conn) -> list:
    query = f"""
            SELECT REGEXP_SUBSTR(table_name, '\\d{{4}}$') AS year
            FROM all_tables
            WHERE table_name LIKE 'NUM06_%'
            AND owner = '{owner}'
            AND REGEXP_LIKE(table_name, 'NUM06_\\d{{4}}$')
            ORDER BY year
            """
    df = pd.read_sql(query, con=conn)
    df.columns = [col.lower() for col in df.columns]
    print(f"연도 추출 컬럼들: {df.columns}")
    print(f"연도 리스트 갯수: {len(df)}개")

    return df["year"].astype(str).tolist()



years = get_available_years(db.conn)

# 연도별 예측 수행
for y in years:
    source_table = f"LIBRA.NUM06_{y}"
    builder = SCRTableBuilder(
        conn=db.conn,
        engine=db.engine,
        year=y,
        source_table=source_table
    )
    success = builder.run()
    if not success:
        print(f"[오류] {y}년도 예측 테이블 생성 실패")

# 첫번째 모델을 통한 데이터셋 제작
for y in years:
    table_name = f"NUM08_{y}"
    updater = SCRTableUpdater(conn=db.conn, engine=db.engine, year=y, table_name=table_name)
    success = updater.run()
    if not success:
        print(f"[오류] {y}년도 순위 업데이트 실패")

# DB 연결 종료
db.close()

print("[EstimationFlow] 전체 실행 완료")