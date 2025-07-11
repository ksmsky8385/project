from sklearn.model_selection import train_test_split
from ML_RFR.model import RandomForestModel
from ML_RFR.utils.evaluator import evaluate_metrics  # ← 함수명 수정

class ModelTrainer:
    def __init__(self, model):
        self.model = model

    def train(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)

        # RMSE + MAE 반환
        metrics = evaluate_metrics(y_test, y_pred)
        return metrics
