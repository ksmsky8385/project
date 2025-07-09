from sklearn.ensemble import RandomForestRegressor
from ML_RFR.config import RFR_PARAMS

class RandomForestModel:
    def __init__(self):
        self.model = RandomForestRegressor(**RFR_PARAMS)

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)
