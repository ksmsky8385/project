from sklearn.metrics import mean_squared_error
import numpy as np

class Evaluator:
    @staticmethod
    def rmse(y_true, y_pred) -> float:
        return np.sqrt(mean_squared_error(y_true, y_pred))