from sklearn.model_selection import train_test_split
from ML_RFR.utiles.validator import validate_columns
from ML_RFR.utiles.evaluator import evaluate_metrics
from ML_RFR.model import RandomForestModel

class ModelTrainer:
    def __init__(self, rfr_params_by_cluster: dict, input_cols: list):
        self.rfr_params_by_cluster = rfr_params_by_cluster
        self.required_input_cols = input_cols
        self.models_by_cluster = {}

    def train(self, X, y):
        """
        전체 데이터에 대해 단일 모델 훈련
        """
        validate_columns(X, self.required_input_cols)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model_wrapper = RandomForestModel(cluster_id="full", params_dict=self.rfr_params_by_cluster)
        model_wrapper.fit(X_train, y_train)
        model = model_wrapper.get_model()

        y_pred = model.predict(X_test)
        self.models_by_cluster["full"] = model

        return evaluate_metrics(y_test, y_pred)

    def train_by_cluster(self, df, input_cols, target_col, cluster_col="cluster_id"):
        """
        클러스터별로 개별 모델을 훈련하고 저장

        Returns:
        - metrics_dict: 클러스터별 성능 지표 딕셔너리
        """
        validate_columns(df, input_cols + [target_col])

        metrics_dict = {}
        self.models_by_cluster = {}

        for cluster_id in sorted(df[cluster_col].unique()):
            sub_df = df[df[cluster_col] == cluster_id]
            X = sub_df[input_cols]
            y = sub_df[target_col]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            model_wrapper = RandomForestModel(cluster_id=cluster_id, params_dict=self.rfr_params_by_cluster)
            model_wrapper.fit(X_train, y_train)
            model = model_wrapper.get_model()

            y_pred = model.predict(X_test)
            self.models_by_cluster[cluster_id] = model
            metrics_dict[cluster_id] = evaluate_metrics(y_test, y_pred)

        return metrics_dict
