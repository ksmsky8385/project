import os
import json
from core_utiles.OracleDBConnection import OracleDBConnection
from Predictor.TableBuilder import TableBuilder

class Controller:
    def __init__(self, config_name: str):
        # 컨피그 경로 구성
        self.config_path = os.path.join(
            os.path.dirname(__file__), "..", "_Configs", config_name
        )
        self.config = self.load_config()
        self.db = OracleDBConnection()

    def load_config(self) -> dict:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            print(f"[INFO] 컨피그 로딩 완료 ➜ {self.config_path}")
            return config
        except Exception as e:
            print(f"[ERROR] 컨피그 로딩 실패 ➜ {e}")
            raise

    def run(self):
        print("[Controller] Oracle DB 연결 시작")
        self.db.connect()

        print("[Controller] 예측 파이프라인 시작")
        builder = TableBuilder(
            config=self.config,
            conn=self.db.conn,
            engine=self.db.engine
        )
        builder.run()

        print("[Controller] Oracle DB 연결 종료")
        self.db.close()