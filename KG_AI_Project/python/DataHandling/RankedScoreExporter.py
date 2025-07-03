import pandas as pd
import os

class RankedScoreExporter:
    def __init__(self, score_path, mapping_path, output_dir):
        self.score_path = score_path
        self.mapping_path = mapping_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        try:
            score_df = pd.read_csv(self.score_path)
            mapping_df = pd.read_csv(self.mapping_path)
        except Exception as e:
            print(f"❌ 파일 로딩 실패: {e}")
            return

        if not {"Institution", "Score", "Year"}.issubset(score_df.columns):
            print("❌ 대학평가점수 CSV의 컬럼명이 예상과 다릅니다.")
            return
        if not {"Institution", "Korean_Name"}.issubset(mapping_df.columns):
            print("❌ 대학명 매핑표 CSV의 컬럼명이 예상과 다릅니다.")
            return

        # 1️⃣ 대학명 매핑
        score_df = score_df.merge(mapping_df, on="Institution", how="left")

        # 2️⃣ 한국명 없는 경우 처리
        missing = score_df[score_df["Korean_Name"].isna()]
        if not missing.empty:
            print(f"⚠️ 매핑되지 않은 대학명 수: {len(missing)}")
            print("🔎 미매핑 대학명:")
            for name in sorted(missing["Institution"].unique()):
                print(f"   - {name}")
            score_df = score_df.dropna(subset=["Korean_Name"])  # 매핑 실패 제거

        # 3️⃣ 연도별 분할
        years = sorted(score_df["Year"].unique())
        for year in years:
            year_df = score_df[score_df["Year"] == year].copy()
            year_df = year_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
            year_df["Rank"] = year_df.index + 1

            # 4️⃣ 컬럼 재정렬 및 이름 변경
            final_df = year_df[["Year", "Rank", "Korean_Name", "Score"]].rename(columns={
                "Year": "연도",
                "Rank": "순위",
                "Korean_Name": "학교명",
                "Score": "점수"
            })

            filename = f"Num00_상위대학평가점수_{year}.csv"
            file_path = os.path.join(self.output_dir, filename)
            final_df.to_csv(file_path, index=False, encoding="utf-8-sig")
            print(f"✅ 저장 완료: {filename}")