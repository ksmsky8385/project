import joblib
from core_utiles.config_loader import MODEL_NUM01_SAVE_PATH

class ModelLoader:
    def __init__(self, path=MODEL_NUM01_SAVE_PATH):
        self.path = path

    def load(self):
        print(f"[모델 로딩] {self.path}")
        return joblib.load(self.path)
