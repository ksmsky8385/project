import os
import pandas as pd

# 경로 및 파일 설정
BASE_DIR = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"
NUM06_PREFIX = "Num06_종합데이터_"
NUM00_PREFIX = "Num00_상위대학평가점수_"
YEARS = list(range(2014, 2025))
TOP_N = 20  # 출력할 상관관계 상위/하위 컬럼 개수
EXCLUDE_COLUMNS = ["YR"]  # 분석에서 제외할 컬럼

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
    return sorted(set.intersection(*column_sets))

def load_score_filtered_data(common_cols):
    merged = []
    for year in YEARS:
        path06 = os.path.join(BASE_DIR, f"{NUM06_PREFIX}{year}.csv")
        path00 = os.path.join(BASE_DIR, f"{NUM00_PREFIX}{year}.csv")

        df06 = pd.read_csv(path06, encoding="utf-8")
        df00 = pd.read_csv(path00, encoding="utf-8")

        df06.columns = df06.columns.str.strip()
        df00.columns = df00.columns.str.strip()

        df06 = drop_duplicate_columns(df06)
        df00 = drop_duplicate_columns(df00)

        df06["YR"] = year
        df00["YR"] = year

        df06["SNM"] = df06["SNM"].astype(str).str.strip()
        df00["SNM"] = df00["SNM"].astype(str).str.strip()

        df06_sub = df06[["SNM"] + list(common_cols)].copy()
        df00_sub = df00[["SNM", "SCR"]].copy()

        df06_sub = drop_duplicate_columns(df06_sub)
        df00_sub = drop_duplicate_columns(df00_sub)

        merged_df = pd.merge(df06_sub, df00_sub, on="SNM")
        merged.append(merged_df)

    return pd.concat(merged, ignore_index=True)

def analyze_correlations(df, common_cols, target="SCR", top_n=TOP_N, exclude_columns=EXCLUDE_COLUMNS):
    df = drop_duplicate_columns(df)

    # 숫자형 컬럼 중에서 제외 항목을 제거
    numeric_cols = [
        col for col in df[list(common_cols)].select_dtypes(include=["number"]).columns
        if col not in exclude_columns
    ]

    corr = df[numeric_cols + [target]].corr()[target].drop(target).sort_values(ascending=False)

    print("\n[+] SCR과 양의 상관 상위 {}개".format(top_n))
    print(corr.head(top_n).to_string())

    neg_corr = corr[corr < 0].sort_values(ascending=True)
    print("\n[–] SCR과 음의 상관 상위 {}개".format(top_n))
    print(neg_corr.head(top_n).to_string())

if __name__ == "__main__":
    print("[STEP 1] 공통 컬럼 추출 중...")
    common_cols = get_common_columns()
    print("→ 공통 컬럼 개수:", len(common_cols))

    print("[STEP 2] 점수 대학 병합 중...")
    merged_df = load_score_filtered_data(common_cols)
    print("→ 병합 결과:", len(merged_df), "개 대학")

    print("[STEP 3] 상관 분석 중...")
    analyze_correlations(merged_df, common_cols)
