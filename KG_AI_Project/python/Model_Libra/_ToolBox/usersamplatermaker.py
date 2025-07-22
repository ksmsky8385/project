import pandas as pd
import os

# CSV 파일에 들어갈 데이터를 딕셔너리 형태로 정의합니다.
data = {
    'USR_ID': ['1111', '2222', '3333'],
    'USR_PW': ['1111', '2222', '3333'],
    'USR_NAME': ['이순신', '홍길동', '강승민'],
    'USR_SNM': ['부산대학교', '경기대학교', '동국대학교'],
    '1ST_YR': [2021, 2018, 2020],
    '1ST_USR_CPS': [200000, 400000, 0],
    '1ST_USR_LPS': [10, 20, 0],
    '1ST_USR_VPS': [30, 50, 0],
    '2ND_YR': [2022, 2019, 2021],
    '2ND_USR_CPS': [100000, 390000, 0],
    '2ND_USR_LPS': [15, 23, 1],
    '2ND_USR_VPS': [20, 60, 0],
    '3RD_YR': [2023, 2020, 2022],
    '3RD_USR_CPS': [100000, 290000, 0],
    '3RD_USR_LPS': [10, 30, 1],
    '3RD_USR_VPS': [60, 72, 3],
    '4TH_YR': [2024, 2021, 2023],
    '4TH_USR_CPS': [300000, 500000, 0],
    '4TH_USR_LPS': [30, 40, 2],
    '4TH_USR_VPS': [70, 90, 5]
}

df = pd.DataFrame(data)

save_directory = 'D:/workspace/project/KG_AI_Project/resource/csv_files'


os.makedirs(save_directory, exist_ok=True)

# 3. 파일 이름과 경로를 결합하여 최종 파일 경로를 만듭니다.

file_name = '유저데이터.csv'

full_path = os.path.join(save_directory, file_name)


df.to_csv(full_path, index=False, encoding='utf-8-sig')

print(f"'{full_path}' 파일이 성공적으로 생성되었습니다.")