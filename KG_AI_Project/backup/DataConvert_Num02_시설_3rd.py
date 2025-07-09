import pandas as pd
import os

# 기본통계_시설.xlsx 데이터시트 csv 파일 변환 스크립트 세번째.
# 2018년도까지의 파일 컬럼 수 조절 및 컬럼명 통일 코드.

# 원본 파일 폴더
source_dir = r'D:\workspace\project\KG_AI_Project\python\DataConvert'
# 저장할 폴더 (동일 경로에 덮어쓰기 또는 새 폴더 사용 가능)
output_dir = source_dir  # 덮어쓰기 시 동일 경로

# 대상 연도
for year in range(2014, 2019):
    filename = f'Num02_시설_{year}.csv'
    filepath = os.path.join(source_dir, filename)

    # CSV 불러오기
    df = pd.read_csv(filepath, encoding='utf-8-sig')

    # 컬럼 삭제
    df.drop(['업무용컴퓨터수', '이용자용컴퓨터수'], axis=1, inplace=True)

    # 컬럼명 변경
    df.rename(columns={'총 보유컴퓨터수': '정보화기기수'}, inplace=True)

    # 저장
    output_path = os.path.join(output_dir, filename)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

print("✅ 2014~2018 시설 CSV → 13개 컬럼으로 재구성 완료!")