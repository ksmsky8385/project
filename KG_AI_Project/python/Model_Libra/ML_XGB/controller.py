from ML_XGB.config import Config
from ML_XGB.fetcher import DataFetcher
from ML_XGB.cleaner import DataCleaner
from ML_XGB.model import XGBModel
from ML_XGB.trainer import ModelTrainer
from ML_XGB.predictor import XGBPredictor
from ML_XGB.utils.exporter import save_model
from core_utiles.config_loader import ORACLE_CLIENT_PATH, MODEL_NUM02_SAVE_PATH
from core_utiles.OracleDBConnection import OracleDBConnection
import oracledb
import pandas as pd

class XGBPipelineController:
    def __init__(self):
        self.db = OracleDBConnection()
        self.conn = None

    def setup_oracle_client(self):
        try:
            oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_PATH)
            print(f"[Oracle Init] Instant Client 경로: {ORACLE_CLIENT_PATH}")
        except Exception as e:
            raise RuntimeError(f"[ERROR] Oracle 클라이언트 초기화 실패 → {e}")

    def run(self):
        print("[START] XGB 모델 파이프라인 실행")
        self.setup_oracle_client()
        self.db.connect()
        self.conn = self.db.conn

        # 1. 데이터 로드 및 전처리
        fetcher = DataFetcher(self.conn)
        YEARS_FOR_XGB = range(2014, 2025)
        df = fetcher.get_panel_data(years=YEARS_FOR_XGB)
        df = DataCleaner().clean(df)

        # 2. 피처 생성 (슬라이딩 시계열)
        df["SCR_EST_t-1"] = df.groupby("ID")["SCR_EST"].shift(1)
        df["SCR_EST_t-2"] = df.groupby("ID")["SCR_EST"].shift(2)
        df = df.dropna().reset_index(drop=True)

        features = ["SCR_EST_t-1", "SCR_EST_t-2"]
        target = Config.TARGET_COLUMN  # SCR_EST

        # 3. 모델 학습
        model = XGBModel().build()
        trainer = ModelTrainer(model, MODEL_NUM02_SAVE_PATH)
        trainer.train(df, features, target)
        save_model(model, MODEL_NUM02_SAVE_PATH)
        print(f"[완료] 모델 저장: {MODEL_NUM02_SAVE_PATH}")

        # 4. 단일 예측 예시
        print("[예측테스트] 단일 대학 예측 예시 시작")

        school_name = "전북대학교"
        years = list(range(2014, 2025))

        # predictor: multi_horizon only needs df, so engine 인자만 전달
        predictor = XGBPredictor(model, self.db.engine)

        # 2024 실데이터 확인
        baseline = fetcher.load_table("LIBRA.NUM08_2024")
        row24 = baseline.query("SNM == @school_name").iloc[0]
        print(f"[2024 기준] {school_name} SCR_EST: {row24['SCR_EST']:.4f}, RK_EST: {row24['RK_EST']}")

        # 1) 시계열 데이터 수집
        seqs = []
        for y in years:
            tbl = f"LIBRA.NUM08_{y}"
            sql = f"""
                SELECT ID, YR, SCR_EST, SNM
                FROM {tbl}
                WHERE SNM = :school
            """
            try:
                part = pd.read_sql(sql, self.db.engine, params={"school": school_name})
                part["YR"] = y
                seqs.append(part)
            except Exception as e:
                print(f"[스킵] {tbl} 조회 실패: {e}")

        if not seqs:
            print(f"[예측 불가] {school_name} 시계열 데이터 없음")
            self.db.close()
            return

        # 2) 합치고 컬럼명 정리
        df_seq = pd.concat(seqs).sort_values("YR").reset_index(drop=True)

        # 대소문자 통일 + 중복 컬럼 제거 (뒤에 추가된 컬럼을 살림)
        df_seq.columns = [col.upper() for col in df_seq.columns]
        df_seq = df_seq.loc[:, ~df_seq.columns.duplicated(keep='last')]

        # 필수 컬럼 누락 검사
        required_cols = ["ID", "YR", "SCR_EST", "SNM"]
        missing = [col for col in required_cols if col not in df_seq.columns]
        if missing:
            raise ValueError(f"[ERROR] 필수 컬럼 누락: {missing}")


        # 3) shift 피처 생성 & NAN 제거
        df_seq["SCR_EST_t-1"] = df_seq["SCR_EST"].shift(1)
        df_seq["SCR_EST_t-2"] = df_seq["SCR_EST"].shift(2)
        df_seq = df_seq.dropna().reset_index(drop=True)

        if df_seq.empty:
            print(f"[예측 불가] {school_name} 과거 점수 부족")
        else:
            # 4) multi horizon 예측
            preds = predictor.multi_horizon_predict(df_seq, horizon=2)
            for yr, sc in preds:
                print(f"[{yr} 예측] {school_name} 예측 SCR_EST: {sc:.4f}")

        self.db.close()