import pandas as pd

# 기본통계_시설.xlsx 데이터시트 csv 파일 변환 스크립트 첫번째.
# 2018년도 이후 데이터 컬럼범위 변경으로 인한 2018년도까지 선 저장 코드.

# 파일 경로
excel_file = r'D:\workspace\project\KG_AI_Project\resource\raw_files\기본통계_시설.xlsx'

# CSV 고정 컬럼명 (총 15개)
columns = [
    '연도','번호','학교명','학교유형','설립','지역','대학규모',
    '도서관건물연면적','총열람석수','업무용컴퓨터수','이용자용컴퓨터수',
    '총 보유컴퓨터수','연면적','재학생수','재학생 1인당 도서관건물 연면적'
]

# 전체 엑셀 로드
df = pd.read_excel(excel_file, header=None, engine='openpyxl')

# 공통 열: A~G열 (0~6)
common_cols = df.iloc[7:, 0:6]

# 연도 범위 정의
for i, year in enumerate(range(2014, 2019)):  # 2014 ~ 2018
    start_col = 6 + i * 8
    end_col = start_col + 8

    # 연도별 열 슬라이싱
    year_cols = df.iloc[7:, start_col:end_col]

    # 병합 & 연도 삽입
    year_data = pd.concat([common_cols, year_cols], axis=1)
    year_data.insert(0, '연도', year)

    # 열 수 맞춰 컬럼명 지정 (15개)
    year_data.columns = columns

    # 마지막 열만 float 형식 지정
    year_data[columns[-1]] = pd.to_numeric(year_data[columns[-1]], errors='coerce').astype(float)

    # 저장
    filename = f'Num02_시설_{year}.csv'
    year_data.to_csv(filename, index=False, encoding='utf-8-sig')

print("✅ 모든 연도별 시설 통계 CSV 변환 완료! (15컬럼 정렬)")