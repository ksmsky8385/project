import pandas as pd

# 기존 CSV 파일(cp949 인코딩) 불러오기
df = pd.read_csv("D:/workspace/project/data/서울도서관 장서 대출목록 (2025년 05월).csv", encoding="cp949")

# 새로운 파일로 utf-8 인코딩 저장
df.to_csv("D:/workspace/project/data/seoul_books_utf8.csv", encoding="utf-8-sig", index=False)

# 분류번호가 공란인 도서 제외 필터링
df_filtered = df[df["주제분류번호"].notna() & (df["주제분류번호"].astype(str).str.strip() != "")]

# 새로운 필터링된 파일로 저장
df_filtered.to_csv("D:/workspace/project/data/filtered_books_utf8.csv", encoding="utf-8-sig", index=False)
