from ML_RFR.config import FILTERED_TABLE, INPUT_COLUMNS, TARGET_COLUMN
from ML_RFR.fetcher import DataFetcher
from ML_RFR.cleaner import DataCleaner
from ML_RFR.model import RandomForestModel
from ML_RFR.trainer import ModelTrainer
from ML_RFR.predictor import ModelPredictor
from ML_RFR.utils.exporter import save_model
from core_utiles.config_loader import MODEL_NUM01_SAVE_PATH
import oracledb

class RFRPipelineController:
    def __init__(self, conn, oracle_client_path):
        self.conn = conn
        self.oracle_client_path = oracle_client_path

    def setup_oracle_client(self):
        try:
            oracledb.init_oracle_client(lib_dir=self.oracle_client_path)
            print(f"[Oracle Init] Instant Client 경로: {self.oracle_client_path}")
        except Exception as e:
            raise RuntimeError(f"[ERROR] Oracle 클라이언트 초기화 실패 → {e}")

    def run(self):
        print("[START] RFR 모델 훈련 및 예측 파이프라인")

        # 1. 데이터 수집
        fetcher = DataFetcher(self.conn)
        df_raw = fetcher.load_table(FILTERED_TABLE)

        # 2. 데이터 전처리
        cleaner = DataCleaner()
        df_clean = cleaner.clean_numeric(df_raw, INPUT_COLUMNS + [TARGET_COLUMN])

        X = df_clean[INPUT_COLUMNS]
        y = df_clean[TARGET_COLUMN]

        # 3. 모델 학습
        model = RandomForestModel()
        trainer = ModelTrainer(model)
        rmse = trainer.train(X, y)
        print(f"[훈련 완료] RMSE: {rmse:.2f}")

        # 4. 모델 저장
        save_model(model.model, path=MODEL_NUM01_SAVE_PATH)
        print(f"[저장 완료] 모델 저장 위치: {MODEL_NUM01_SAVE_PATH}")

        # 5. 단일 예측 테스트
        school_name = "가야대학교"
        table_name = "LIBRA.NUM06_2014"
        predictor = ModelPredictor(model.model, self.conn, INPUT_COLUMNS)
        score, features = predictor.predict_by_school(school_name, table_name)
        print(f"[예측테스트] {school_name} SCR: {score:.2f}점")
        print(features)
