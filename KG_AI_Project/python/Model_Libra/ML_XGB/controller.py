from ML_XGB.config import Config
from ML_XGB.fetcher import DataFetcher
from ML_XGB.cleaner import DataCleaner
from ML_XGB.model import XGBModel
from ML_XGB.trainer import ModelTrainer
from ML_XGB.predictor import XGBPredictor
from ML_XGB.utiles.exporter import save_model
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

        # 2. 피처 생성 (t-0 ~ t-(n-1))
        df = df.sort_values(["ID", "YR"]).reset_index(drop=True)
        for i in range(Config.ROLLING_WINDOW):
            df[f"SCR_EST_t-{i}"] = df.groupby("ID")["SCR_EST"].shift(i)

        df = df.dropna().reset_index(drop=True)
        features = [f"SCR_EST_t-{i}" for i in range(Config.ROLLING_WINDOW)]
        target = Config.TARGET_COLUMN

        # 3. 모델 학습
        model = XGBModel().build()
        trainer = ModelTrainer(model)
        trainer.train(df, features, target)
        save_model(model, MODEL_NUM02_SAVE_PATH)
        print(f"[완료] 모델 저장: {MODEL_NUM02_SAVE_PATH}")

        # 4. 단일 예측 예시
        print("[예측테스트] 단일 대학 예측 예시 시작")
        school_name = "서울대학교"
        years = list(range(2014, 2025))

        predictor = XGBPredictor(model, self.db.engine)

        # 실측 출력
        baseline = fetcher.load_table("LIBRA.NUM08_2024")
        row24 = baseline.query("SNM == @school_name").iloc[0]
        print(f"[2024 기준] {school_name} SCR_EST: {row24['SCR_EST']:.4f}, RK_EST: {row24['RK_EST']}")

        # 시계열 수집
        seqs = []
        for y in years:
            table = f"LIBRA.NUM08_{y}"
            query = f"""
                SELECT ID, YR, SCR_EST, SNM
                FROM {table}
                WHERE SNM = :school
            """
            try:
                part = pd.read_sql(query, self.db.engine, params={"school": school_name})
                part["YR"] = y
                seqs.append(part)
            except Exception as e:
                print(f"[스킵] {table} 조회 실패: {e}")

        if not seqs:
            print(f"[예측 불가] {school_name} 시계열 없음")
            self.db.close()
            return

        df_seq = pd.concat(seqs).sort_values("YR").reset_index(drop=True)
        df_seq.columns = [col.upper() for col in df_seq.columns]
        df_seq = df_seq.loc[:, ~df_seq.columns.duplicated(keep='last')]

        required = ["ID", "YR", "SCR_EST", "SNM"]
        missing = [c for c in required if c not in df_seq.columns]
        if missing:
            raise ValueError(f"[ERROR] 필수 컬럼 누락: {missing}")

        # 피처 생성: t-0 ~ t-(n-1)
        df_seq = df_seq.sort_values(["ID", "YR"]).reset_index(drop=True)
        for i in range(Config.ROLLING_WINDOW):
            df_seq[f"SCR_EST_t-{i}"] = df_seq.groupby("ID")["SCR_EST"].shift(i)

        df_seq = df_seq.dropna().reset_index(drop=True)

        if df_seq.empty:
            print(f"[예측 불가] {school_name} 예측 입력 부족")
        else:
            next_year, score = predictor.predict_next_year(df_seq)
            print(f"[{next_year} 예측] {school_name} 예측된 평가점수: {score:.4f}점")

        self.db.close()
