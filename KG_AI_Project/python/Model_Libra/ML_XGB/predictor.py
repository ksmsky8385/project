import pandas as pd

class XGBPredictor:
    def __init__(self, model, engine=None):
        self.model = model
        self.engine = engine

    def multi_horizon_predict(self, df: pd.DataFrame, horizon: int = 1):
        df = df.copy().reset_index(drop=True)
        preds = []

        # 시작 시점의 t-1, t-2 값을 분리 보존
        scr_t1 = float(df.iloc[-1]["SCR_EST"])             # 최신 실측 → t-1
        scr_t2 = float(df.iloc[-1]["SCR_EST_t-1"])         # 그 이전 실측 → t-2

        for i in range(horizon):
            pred_year = int(df.iloc[-1]["YR"]) + 1

            feat = pd.DataFrame({
                "SCR_EST_t-1": [scr_t1],
                "SCR_EST_t-2": [scr_t2]
            })

            y_pred = float(self.model.predict(feat)[0])
            preds.append((pred_year, y_pred))

            # 다음 반복을 위해 값 밀기 (예측값 -> t-1, 기존 t-1 -> t-2)
            scr_t2 = scr_t1
            scr_t1 = y_pred

            # 예측값을 df에 추가
            last = df.iloc[-1]
            new_row = {
                "ID": last["ID"],
                "SNM": last["SNM"],
                "YR": pred_year,
                "SCR_EST": y_pred,
                "SCR_EST_t-1": scr_t1,
                "SCR_EST_t-2": scr_t2
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            print(f"[DEBUG] 입력 features:\n{feat}")
            y_pred = float(self.model.predict(feat)[0])
            print(f"[DEBUG] 예측값: {y_pred}")

        return preds

