import os
import pandas as pd

def convert_headers(csv_path, mapping_path, direction):
    # 파일 경로 설정
    base_dir = os.path.dirname(csv_path)
    base_name = os.path.basename(csv_path)
    name, ext = os.path.splitext(base_name)

    # 🔄 방향별 파일명
    suffix = '_한글헤더' if direction == 'eng_to_kor' else '_영문헤더'
    output_csv = os.path.join(base_dir, f"{name}{suffix}{ext}")

    # 매핑표 불러오기
    mapping_df = pd.read_csv(mapping_path, encoding='utf-8-sig')
    kor_to_eng = dict(zip(mapping_df.iloc[:, 0].astype(str),
                        mapping_df.iloc[:, 1].astype(str).str.upper()))
    eng_to_kor = dict(zip(mapping_df.iloc[:, 1].astype(str).str.upper(),
                        mapping_df.iloc[:, 0].astype(str)))
    mapping = eng_to_kor if direction == 'eng_to_kor' else kor_to_eng

    # 원본 CSV 불러오기
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    original_columns = df.columns.tolist()
    new_columns = []

    for col in original_columns:
        parts = col.upper().split('_') if direction == 'eng_to_kor' else col.split('_')
        translated_parts = [mapping.get(part, part) for part in parts]
        new_col = '_'.join(translated_parts)
        new_columns.append(new_col)

    df.columns = new_columns
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"✅ 헤더 변환 완료 → {output_csv}")


if __name__ == "__main__":
    convert_headers(
        csv_path=r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data\필터링데이터.csv",
        mapping_path=r"D:\workspace\project\KG_AI_Project\resource\csv_files\헤더약어매핑표.csv",
        direction='eng_to_kor'  # 또는 'kor_to_eng'
    )