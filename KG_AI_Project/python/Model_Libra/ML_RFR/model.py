from sklearn.ensemble import RandomForestRegressor
from ML_RFR.config import RFR_PARAMS_BY_CLUSTER

class RandomForestModel:
    def __init__(self, cluster_id="full"):
        params = RFR_PARAMS_BY_CLUSTER[cluster_id]
        self.model = RandomForestRegressor(**params)

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)
