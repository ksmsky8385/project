import pandas as pd

# 기본통계_시설.xlsx 데이터시트 csv 파일 변환 스크립트 두번째.
# 2018년도 이후 데이터 컬럼범위 변경 후 저장 코드.

# 파일 경로
excel_file = r'D:\workspace\project\KG_AI_Project\resource\raw_files\기본통계_시설.xlsx'

# CSV 고정 컬럼명 (13개 구조)
columns_2019 = [
    '연도','번호','학교명','학교유형','설립','지역','대학규모',
    '도서관건물연면적','총열람석수','정보화기기수',
    '연면적','재학생수','재학생 1인당 도서관건물 연면적'
]

# 전체 엑셀 로드
df = pd.read_excel(excel_file, header=None, engine='openpyxl')

# 공통 열: A~F열 → 0~6 인덱스
common_cols = df.iloc[7:, 0:6]

# 연도 반복: 2019~2024
for i, year in enumerate(range(2019, 2025)):
    start_col = 46 + i * 6
    end_col = start_col + 6

    # 연도별 열 슬라이싱
    year_cols = df.iloc[7:, start_col:end_col]

    # 병합 & 연도 삽입
    year_data = pd.concat([common_cols, year_cols], axis=1)
    year_data.insert(0, '연도', year)

    # 열 맞춰 컬럼명 지정
    year_data.columns = columns_2019

    # 마지막 열만 float 지정
    year_data[columns_2019[-1]] = pd.to_numeric(year_data[columns_2019[-1]], errors='coerce').astype(float)

    # 저장
    filename = f'Num02_시설_{year}.csv'
    year_data.to_csv(filename, index=False, encoding='utf-8-sig')

print("✅ 2019~2024 시설 통계 CSV 저장 완료! (13컬럼 정렬)")