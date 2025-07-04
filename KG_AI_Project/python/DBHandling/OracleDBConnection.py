import oracledb

class OracleDBConnection:
    def __init__(self, username, password, dsn, client_dir):
        self.username = username
        self.password = password
        self.dsn = dsn
        self.client_dir = client_dir
        self.conn = None
        self.cursor = None
        self._init_client()

    def _init_client(self):
        try:
            oracledb.init_oracle_client(lib_dir=self.client_dir)
        except Exception as e:
            print("❌ Oracle Instant Client 초기화 실패:", e)

    def connect(self):
        try:
            self.conn = oracledb.connect(
                user=self.username,
                password=self.password,
                dsn=self.dsn
            )
            self.cursor = self.conn.cursor()
            print("🔗 Oracle DB 접속 성공")
        except Exception as e:
            print("❌ Oracle DB 연결 실패:", e)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔒 DB 연결 종료")

    def execute_query(self, query):
        if not self.cursor:
            raise Exception("📛 DB 연결이 없습니다. 먼저 connect()를 호출하세요.")
        self.cursor.execute(query)
        return self.cursor.fetchall()