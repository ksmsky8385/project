class Config:
    xgb_params = {
        "n_estimators": 200,
        "max_depth": 5,
        "learning_rate": 0.05,
        "random_state": 42
    }

    model_path = "ML_XGB/models/model_xgb_v1.0.pkl"
    TARGET_COLUMN = "SCR_EST"