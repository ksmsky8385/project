import os
import pandas as pd
import oracledb

class CSVToOracleUploader:
    def __init__(self, username, password, dsn, csv_dir, client_dir):
        oracledb.init_oracle_client(lib_dir=client_dir)

        self.username = username
        self.password = password
        self.dsn = dsn
        self.csv_dir = csv_dir
        self.file_list = [f for f in os.listdir(csv_dir) if f.endswith(".csv")]

    def run(self):
        try:
            conn = oracledb.connect(user=self.username, password=self.password, dsn=self.dsn)
            cursor = conn.cursor()
            print("🔗 Oracle DB 접속 성공\n")

            for filename in self.file_list:
                file_path = os.path.join(self.csv_dir, filename)
                df = pd.read_csv(file_path, encoding="utf-8")

                # 컬럼명 byte 수 검사 (30 초과만 출력)
                for col in df.columns:
                    byte_len = len(col.encode('utf-8'))
                    if byte_len > 30:
                        print(f"⚠️ [파일: {filename}] 컬럼명 '{col}' → {byte_len} bytes (30 초과)")


                # 테이블명: 번호_데이터_연도.csv → 번호_연도
                name_parts = filename.replace('.csv', '').split('_')
                table_name = f"{name_parts[0]}_{name_parts[2]}".upper()

                columns = df.columns.tolist()
                col_defs = ', '.join([f'"{col}" VARCHAR2(4000)' for col in columns])
                create_sql = f'CREATE TABLE "{table_name}" ({col_defs})'

                try:
                    # 🗑️ 테이블이 존재한다면 삭제하고 생성
                    try:
                        cursor.execute(f'DROP TABLE "{table_name}"')
                        print(f"🗑️ 기존 테이블 {table_name} 삭제 완료")
                    except oracledb.DatabaseError as e:
                        if "ORA-00942" in str(e):
                            print(f"ℹ️ 테이블 {table_name} 없음 (DROP 생략)")
                        else:
                            print(f"❌ DROP TABLE 오류: {e}")
                            raise

                    # 🧱 테이블 생성
                    cursor.execute(create_sql)
                    print(f"🧱 테이블 {table_name} 생성 완료")

                except oracledb.DatabaseError as e:
                    print(f"❌ 테이블 생성 오류 ({table_name}): {e}")
                    continue


                placeholders = ', '.join([f':{i+1}' for i in range(len(columns))])
                col_names = ', '.join([f'"{col}"' for col in columns])
                insert_sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'
                data = [tuple(row) for row in df.values]

                try:
                    cursor.executemany(insert_sql, data)
                    conn.commit()
                    print(f"📥 {filename} → {table_name} 테이블에 {len(data)}건 삽입 완료\n")
                except Exception as e:
                    print(f"❌ {filename} 삽입 오류: {e}\n")

            cursor.close()
            conn.close()
            print("✅ 전체 파일 처리 및 연결 종료")

        except oracledb.DatabaseError as e:
            print("❌ Oracle 연결 오류: ", e)