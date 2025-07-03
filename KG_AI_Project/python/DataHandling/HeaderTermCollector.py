import os
import csv
import pandas as pd
from typing import Set

class HeaderTermCollector:
    def __init__(self, csv_dir: str, encoding: str = "utf-8-sig"):
        self.csv_dir = csv_dir
        self.encoding = encoding
        self.all_columns: Set[str] = set()
        self.all_terms: Set[str] = set()

    def collect(self):
        for filename in os.listdir(self.csv_dir):
            if filename.endswith(".csv"):
                path = os.path.join(self.csv_dir, filename)
                try:
                    df = pd.read_csv(path, nrows=0, encoding=self.encoding)
                    self.all_columns.update(df.columns)
                except Exception as e:
                    print(f"⚠️ [{filename}] → 컬럼 로딩 실패: {e}")

    def tokenize(self, delimiter: str = "_"):
        for col in self.all_columns:
            tokens = col.split(delimiter)
            for t in tokens:
                if t.strip():
                    self.all_terms.add(t.strip())

    def run(self, print_summary=True):
        self.collect()
        self.tokenize()
        if print_summary:
            print(f"✅ 총 {len(self.all_columns)}개 컬럼명 수집")
            print(f"🧩 총 {len(self.all_terms)}개 유니크 토큰 단어 수집\n")
            # for term in sorted(self.all_terms):
            #     print(f" - {term}")

    def save_terms(self, path):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["한글헤더"])  # 첫 번째 열 이름
            for term in sorted(self.all_terms):
                writer.writerow([term])
        print(f"📂 저장경로 : {path}")
        print(f"💾 헤더 단어 목록 CSV 저장 완료")