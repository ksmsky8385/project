import joblib

def save_model(model, path):
    joblib.dump(model, path)
