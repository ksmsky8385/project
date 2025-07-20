from xgboost import XGBRegressor
from ML_XGB.config import Config

class XGBModel:
    def __init__(self):
        self.params = Config.xgb_params

    def build(self) -> XGBRegressor:
        return XGBRegressor(**self.params)
