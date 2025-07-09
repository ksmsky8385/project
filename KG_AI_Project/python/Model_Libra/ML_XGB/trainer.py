import pandas as pd
from sklearn.model_selection import train_test_split
from ML_XGB.utils.evaluator import Evaluator

class ModelTrainer:
    def __init__(self, model):
        self.model = model

    def train(self, df: pd.DataFrame, features: list, target: str) -> float:
        X = df[features]
        y = df[target]

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        print("[학습 완료] 모델 피팅 완료")

        y_pred = self.model.predict(X_val)
        rmse = Evaluator.rmse(y_val, y_pred)
        print(f"[검증 RMSE] {rmse:.4f}")

        return rmse
