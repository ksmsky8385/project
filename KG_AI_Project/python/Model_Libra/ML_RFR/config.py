# 입력 컬럼 및 예측 타깃 정의
INPUT_COLUMNS = [
    "APS_APS", "BGT_MCT", "BGT_UBGT", "BPS_BPS", "BR_BCNT_SUM",
    "CPSS_CPS", "EHS_EHS", "FACLT_EQP_TPC", "FACLT_LAS", "FACLT_RS_TRS",
    "LBRT_USTL", "LPK_LPK", "LPS_LPS", "LS_LB_SUM", "LS_LU_SUM",
    "SPK_SPK", "STL_MCT", "STL_USTL", "VPS_VPS", "VUC_UC_LUC"
    ]
TARGET_COLUMN = "SCR"
FILTERED_TABLE = "LIBRA.FILTERED"

# RFR 하이퍼파라미터
RFR_PARAMS = {
    "n_estimators": 500,
    "max_depth": 15,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "max_features": "sqrt",
    "random_state": 42,
    "n_jobs": -1
}

