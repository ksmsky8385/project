from ML_XGB.config import Config
from ML_XGB.utils.validator import validate_columns
import pandas as pd

class XGBPredictor:
    def __init__(self, model, engine=None):
        self.model = model
        self.engine = engine
        self.window = Config.ROLLING_WINDOW
        self.features = [f"SCR_EST_t-{i}" for i in range(self.window)]  # t-0 ~ t-(n-1)

    def predict_next_year(self, df: pd.DataFrame):
        df = df.copy().sort_values("YR").reset_index(drop=True)
        latest_year = int(df.iloc[-1]["YR"])
        next_year = latest_year + 1

        # 피처 유효성 검사
        validate_columns(df, self.features + ["ID", "SNM", "YR"])

        # 입력 피처 추출
        feat = pd.DataFrame({col: [df.iloc[-1][col]] for col in self.features})

        # 예측 수행
        y_pred = float(self.model.predict(feat)[0])

        # 디버그 출력
        print(f"[DEBUG] 입력 피처:\n{feat}")
        print(f"[DEBUG] 예측 연도: {next_year}, 예측값: {y_pred:.4f}")

        return next_year, y_pred
