from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from ML_RFR.utils.evaluator import evaluate_metrics

class ModelTrainer:
    def __init__(self, rfr_params_by_cluster: dict):
        self.scaler = None
        self.models_by_cluster = {}
        self.rfr_params_by_cluster = rfr_params_by_cluster

    def train(self, X, y, scale=True):
        """
        전체 데이터에 대해 단일 모델 훈련
        """
        if scale:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        params_full = self.rfr_params_by_cluster.get("full", self.rfr_params_by_cluster[0])
        model = RandomForestRegressor(**params_full)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        self.models_by_cluster["full"] = model
        metrics = evaluate_metrics(y_test, y_pred)
        return metrics

    def train_by_cluster(self, df, input_cols, target_col, cluster_col="cluster_id", scale=True):
        """
        클러스터별로 개별 모델을 훈련하고 저장

        Returns:
        - metrics_dict: 클러스터별 성능 지표 딕셔너리
        """
        metrics_dict = {}
        self.models_by_cluster = {}

        for cluster_id in sorted(df[cluster_col].unique()):
            sub_df = df[df[cluster_col] == cluster_id]
            X = sub_df[input_cols]
            y = sub_df[target_col]

            if scale:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
            else:
                X_scaled = X

            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )

            params = self.rfr_params_by_cluster.get(cluster_id, self.rfr_params_by_cluster[0])
            model = RandomForestRegressor(**params)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            self.models_by_cluster[cluster_id] = model
            metrics_dict[cluster_id] = evaluate_metrics(y_test, y_pred)

        return metrics_dict
