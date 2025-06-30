import pandas as pd

df = pd.read_csv("D:/workspace/project/data/filtered_books_utf8.csv", encoding="utf-8")

print(df.head())

kdc_to_major = {
    "300": "사회학과",
    "330": "경제학과",
    "370": "교육학과",
    "420": "수학과",
    "550": "전자공학과",
    "560": "기계공학과",
    "810": "국문과",
    "830": "영문과"
}
