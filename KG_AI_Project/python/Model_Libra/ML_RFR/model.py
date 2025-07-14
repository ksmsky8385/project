from sklearn.ensemble import RandomForestRegressor

class RandomForestModel:
    def __init__(self, cluster_id="full", params_dict=None):
        if params_dict is None:
            raise ValueError("params_dict를 전달해주세요")
        cluster_id = str(cluster_id)
        params = params_dict.get(cluster_id)
        if params is None:
            raise ValueError(f"[ERROR] cluster_id='{cluster_id}'에 해당하는 설정이 없습니다.")
        self.model = RandomForestRegressor(**params)

    def fit(self, X, y): self.model.fit(X, y)
    def predict(self, X): return self.model.predict(X)
    def get_model(self): return self.model
