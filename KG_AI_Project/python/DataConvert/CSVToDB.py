import os
import pandas as pd
import oracledb as cx_Oracle

class CSVToDB:
    def __init__(self, username, password, dsn, csv_dir):
        self.username = username
        self.password = password
        self.dsn = dsn
        self.csv_dir = csv_dir
        self.file_list = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = cx_Oracle.connect(self.username, self.password, self.dsn)
        self.cursor = self.connection.cursor()
        print('🔗 Oracle DB 접속 성공')

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print('\n✅ Oracle DB 연결 종료')

    def create_table_if_needed(self, table_name, columns):
        col_defs = [f'"{col}" VARCHAR2(4000)' for col in columns]
        create_sql = f'CREATE TABLE "{table_name}" ({", ".join(col_defs)})'
        try:
            self.cursor.execute(create_sql)
            print(f'🧱 테이블 {table_name} 생성 완료')
        except cx_Oracle.DatabaseError:
            print(f'⚠️ 테이블 {table_name} 이미 존재하거나 생성 실패 → 건너뜀')

    def insert_data(self, table_name, df):
        columns = df.columns.tolist()
        col_names = ', '.join([f'"{col}"' for col in columns])
        placeholders = ', '.join([f':{i+1}' for i in range(len(columns))])
        insert_sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'
        data = [tuple(row) for row in df.values]

        try:
            self.cursor.executemany(insert_sql, data)
            self.connection.commit()
            print(f'📥 {table_name} 테이블에 {len(data)}건 삽입 완료')
        except Exception as e:
            print(f'❌ {table_name} 삽입 중 오류 발생: {e}')

    def run(self):
        self.connect()

        for filename in self.file_list:
            file_path = os.path.join(self.csv_dir, filename)
            df = pd.read_csv(file_path, encoding='utf-8')  # BOM 제거된 CSV 파일

            # 테이블명 추출: Num01_소장및구독자료_2022.csv → NUM01_소장및구독자료
            name_parts = filename.split('_')
            table_name = f"{name_parts[0]}_{name_parts[1]}".upper()

            self.create_table_if_needed(table_name, df.columns.tolist())
            self.insert_data(table_name, df)

        self.close()