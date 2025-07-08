import pandas as pd
from sklearn.model_selection import train_test_split
import joblib

class ModelTrainer:
    def __init__(self, model, output_path: str):
        self.model = model
        self.output_path = output_path

    def train(self, df: pd.DataFrame, features: list, target: str):
        X = df[features]
        y = df[target]
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)
        self.model.fit(X_train, y_train)
        print("[학습 완료] 모델 피팅 완료")

        joblib.dump(self.model, self.output_path)
        print(f"[저장 완료] {self.output_path} 저장됨")
