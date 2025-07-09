import oracledb
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import numpy as np

oracledb.init_oracle_client(lib_dir=r"C:\Users\user\Desktop\KSM\Tools\instantclient-basic-windows.x64-19.25.0.0.0dbru\instantclient_19_25")

# 1. Oracle 연결 (Thin 모드 사용 예시)
conn = oracledb.connect(
    user="libra",
    password="ksm0923",
    dsn="localhost:1521/XE",  # 예: "localhost:1521/XEPDB1"
    mode=oracledb.DEFAULT_AUTH
)

# 2. FILTERED 테이블 불러오기
query = "SELECT * FROM LIBRA.FILTERED"
df = pd.read_sql(query, con=conn)

# 3. 숫자형 컬럼만 추출
df_numeric = df.select_dtypes(include=["int", "float", "object"])

# 4. NumPy 배열로 변환
data_array = df_numeric.to_numpy()

# 5. 숫자처럼 처리할 컬럼 추출
df_checked = df.copy()
text_cols = ["SNM", "STYP", "FND", "RGN", "USC"]
target_cols = [col for col in df.columns if col not in text_cols]

for col in target_cols:
    try:
        # 쉼표, 공백 제거 등 전처리 추가 가능
        cleaned = df[col].astype(str).str.replace(",", "", regex=False).str.strip()

        # 숫자 변환 시도 (실패 시 예외 발생)
        converted = pd.to_numeric(cleaned, errors="raise")

        # 성공 시 반영
        df_checked[col] = converted

    except Exception as e:
        print(f"[ERROR] 컬럼 '{col}' 변환 실패 → {e}")
        raise SystemExit(f"데이터 변환 중단: '{col}' 열에 숫자가 아닌 값이 존재합니다.")

# 1. X, y 분리 (예: df_checked 사용)
X = df_checked[['APS_APS', 'BGT_MCT', 'BGT_UBGT', 'BPS_BPS', 'BR_BCNT_SUM', 'CPSS_CPS', 'EHS_EHS', 'FACLT_EQP_TPC', 'FACLT_LAS', 'FACLT_RS_TRS', 'LBRT_USTL', 'LPK_LPK', 'LPS_LPS', 'LS_LB_SUM', 'LS_LU_SUM', 'SPK_SPK', 'STL_MCT', 'STL_USTL', 'VPS_VPS', 'VUC_UC_LUC']]
y = df_checked["SCR"]

# 2. 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. 모델 훈련
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# 4. 평가
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print("RMSE:", rmse)

input_columns = [
    "APS_APS", "BGT_MCT", "BGT_UBGT", "BPS_BPS", "BR_BCNT_SUM",
    "CPSS_CPS", "EHS_EHS", "FACLT_EQP_TPC", "FACLT_LAS", "FACLT_RS_TRS",
    "LBRT_USTL", "LPK_LPK", "LPS_LPS", "LS_LB_SUM", "LS_LU_SUM",
    "SPK_SPK", "STL_MCT", "STL_USTL", "VPS_VPS", "VUC_UC_LUC"
]

def predict_scr_by_school_name(school_name):
    query = f"SELECT * FROM LIBRA.NUM06_2014 WHERE TO_CHAR(SNM) = '{school_name}'"
    df_new = pd.read_sql(query, con=conn)

    if df_new.empty:
        raise ValueError(f"대학 '{school_name}'에 해당하는 데이터가 존재하지 않습니다.")

    
    # 전처리 (쉼표 제거, strip 등)
    for col in input_columns:
        df_new[col] = (
            df_new[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        df_new[col] = pd.to_numeric(df_new[col], errors="raise")

    missing_cols = [col for col in input_columns if col not in df_new.columns]
    if missing_cols:
        raise ValueError(f"다음 컬럼이 누락되어 예측이 불가능합니다: {missing_cols}")


    # 입력 피처 추출
    X_new = df_new[input_columns]

    # 예측
    predicted_score = model.predict(X_new)[0]
    print(f"예측된 SCR 점수 ({school_name}): {predicted_score:.2f}")
    return X_new

X_new = predict_scr_by_school_name("동국대학교")
print(X_new)
print("실행 쿼리:", query)

print(X_new[input_columns])