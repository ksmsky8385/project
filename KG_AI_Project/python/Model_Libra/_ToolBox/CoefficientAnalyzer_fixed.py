import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from core_utiles.Mapper import HMP_R


# 경로 및 파일 설정
BASE_DIR = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"
NUM06_PREFIX = "Num06_종합데이터_"
NUM00_PREFIX = "Num00_상위대학평가점수_"
YEARS = list(range(2014, 2025))
TOP_N = 50  # 출력할 상관관계 상위/하위 컬럼 개수
EXCLUDE_COLUMNS = ["YR"]  # 분석에서 제외할 컬럼
TARGET_COLUMN = "SCR"

def get_column_stats(df: pd.DataFrame, col_name: str):
    if col_name not in df.columns:
        return None

    col_data = df[col_name].dropna()

    if col_data.empty:
        return ("N/A", "N/A")

    sample = col_data.iloc[0]
    data_type = type(sample).__name__

    # 자릿수 판별
    try:
        max_val = col_data.max()
        digit = int(pd.np.floor(pd.np.log10(abs(max_val)))) if abs(max_val) >= 1 else 0
        digit_power = f"10^{digit}"
    except Exception:
        digit_power = "N/A"

    return (digit_power, data_type)

def drop_duplicate_columns(df):
    return df.loc[:, ~df.columns.duplicated(keep="first")]

def get_common_columns():
    column_sets = []
    for year in YEARS:
        path = os.path.join(BASE_DIR, f"{NUM06_PREFIX}{year}.csv")
        df = pd.read_csv(path, encoding="utf-8")
        df.columns = df.columns.str.strip()
        df = drop_duplicate_columns(df)
        column_sets.append(set(df.columns))
    # 'SNM'은 명시적으로 병합에 쓰이므로 제외
    return sorted(set.intersection(*column_sets) - {"SNM"})

def analyze_correlations_by_year(common_cols, target=TARGET_COLUMN, top_n=TOP_N, exclude_columns=EXCLUDE_COLUMNS):
    yearly_results = {}

    for year in YEARS:
        path06 = os.path.join(BASE_DIR, f"{NUM06_PREFIX}{year}.csv")
        path00 = os.path.join(BASE_DIR, f"{NUM00_PREFIX}{year}.csv")

        df06 = pd.read_csv(path06, encoding="utf-8")
        df00 = pd.read_csv(path00, encoding="utf-8")

        df06.columns = df06.columns.str.strip()
        df00.columns = df00.columns.str.strip()
        df06 = drop_duplicate_columns(df06)
        df00 = drop_duplicate_columns(df00)

        df06["SNM"] = df06["SNM"].astype(str).str.strip()
        df00["SNM"] = df00["SNM"].astype(str).str.strip()

        df06_sub = df06[["SNM"] + list(common_cols)].copy()
        df00_sub = df00[["SNM", target]].copy()

        df_merged = pd.merge(df06_sub, df00_sub, on="SNM", how="inner")
        numeric_cols = [
            col for col in df_merged.select_dtypes(include=["number"]).columns
            if col != target and col not in exclude_columns
        ]

        corr = df_merged[numeric_cols + [target]].corr()[target].drop(target)
        yearly_results[year] = corr

        # # 연도별 출력 부분 수정 (기존 print → 번역 적용)
        # print(f"\n[{year}년 상관 분석]")

        # print(f"SCR과 상관 상위 {top_n}개")
        # top_corr = corr.sort_values(ascending=False).head(top_n)
        # for k, v in top_corr.items():
        #     print(f"{translate_column(k)}    {v:.6f}")

        # print(f"SCR과 상관 하위 {top_n}개")
        # bottom_corr = corr.sort_values(ascending=True).head(top_n)
        # for k, v in bottom_corr.items():
        #     print(f"{translate_column(k)}    {v:.6f}")


    # 전체 연도 평균 상관 분석
    corr_df = pd.DataFrame(yearly_results)
    mean_corr = corr_df.mean(axis=1)
    # 평균 상관 출력
    print("\n[전체 연도 평균 상관 분석]")
    print(f"평균 상관 상위 {top_n}개")
    top_series = mean_corr.sort_values(ascending=False).head(top_n)
    for k, v in top_series.items():
        print(f"{translate_column(k)}    {v:.6f}")

    print(f"\n평균 상관 하위 {top_n}개")
    bottom_series = mean_corr.sort_values(ascending=True).head(top_n)
    for k, v in bottom_series.items():
        print(f"{translate_column(k)}    {v:.6f}")


    return corr_df

def translate_column(col_name: str) -> str:
    try:
        parts = col_name.split("_")
        translated = [HMP_R(p) for p in parts]
        translated_str = "_".join(translated)
        return f"{translated_str}({col_name})"
    except Exception:
        return col_name  # 에러 시 원본 그대로 출력




# 실행 코드
if __name__ == "__main__":
    print("[STEP 1] 공통 컬럼 추출 중...")
    common_cols = get_common_columns()
    print("→ 공통 컬럼 개수:", len(common_cols))

    print("[STEP 2] 연도별 상관 분석 수행 중...")
    analyze_correlations_by_year(common_cols)
