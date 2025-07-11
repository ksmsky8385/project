from ML_RFR.config import FILTERED_TABLE, INPUT_COLUMNS, TARGET_COLUMN
from ML_RFR.fetcher import DataFetcher
from ML_RFR.cleaner import DataCleaner
from ML_RFR.model import RandomForestModel
from ML_RFR.trainer import ModelTrainer
from ML_RFR.predictor import ModelPredictor
from ML_RFR.utils.exporter import save_model
from ML_RFR.utils.evaluator import evaluate_metrics
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

        # 1. 훈련 데이터 수집 및 전처리
        fetcher = DataFetcher(self.conn)
        df_raw = fetcher.load_table(FILTERED_TABLE)
        cleaner = DataCleaner()
        df_clean = cleaner.clean_numeric(df_raw, INPUT_COLUMNS + [TARGET_COLUMN])
        X = df_clean[INPUT_COLUMNS]
        y = df_clean[TARGET_COLUMN]

        # 2. 모델 훈련
        model = RandomForestModel()
        trainer = ModelTrainer(model)
        metrics = trainer.train(X, y)
        print(f"[훈련 완료] RMSE: {metrics['RMSE']:.4f} / MAE: {metrics['MAE']:.4f} / R2 (정확도): {metrics['R2']:.4f}")

        # 3. 모델 저장
        save_model(model.model, path=MODEL_NUM01_SAVE_PATH)
        print(f"[저장 완료] 모델 저장 위치: {MODEL_NUM01_SAVE_PATH}")

        # 4. 전체 대학 예측 테스트
        table_name = "LIBRA.NUM07_2014"
        predictor = ModelPredictor(model.model, self.conn, INPUT_COLUMNS)
        df_result, test_metrics = predictor.predict_by_table(table_name)

        # 전체 테이블 평균 예측 점수 출력
        print(f"\n[예측테스트] 테이블명 : {table_name.split('.')[-1]}")
        print(f"→ 평균 예측 SCR 점수: {df_result['예측SCR'].mean():.4f}")
        print(f"→ RMSE: {test_metrics['RMSE']:.4f} / MAE: {test_metrics['MAE']:.4f} / R2: {test_metrics['R2']:.4f}")

        # 예측 점수 기준 상위 / 하위 Top5 출력
        print("\n-> 예측 정확도 상위 Top5 (오차율 낮은 순)")
        df_top = df_result.sort_values(by="오차율", ascending=True).head(5)
        for i, row in enumerate(df_top.itertuples(), 1):
            print(f"{i}. {row.SNM} (예측 SCR : {row.예측SCR:.4f}점, 실제 SCR : {row.실제SCR:.4f}점, 오차율 : {row.오차율:.4f}%)")

        print("------------------------------------------------------------")
        print("-> 예측 정확도 하위 Top5 (오차율 높은 순)")
        df_bottom = df_result.sort_values(by="오차율", ascending=False).head(5)
        for i, row in enumerate(df_bottom.itertuples(), 1):
            print(f"{i}. {row.SNM} (예측 SCR : {row.예측SCR:.4f}점, 실제 SCR : {row.실제SCR:.4f}점, 오차율 : {row.오차율:.4f}%)")

