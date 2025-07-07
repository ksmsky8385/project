import os
import pandas as pd

def convert_headers_with_kor_augmented(csv_path, mapping_path):
    # 파일 경로 설정
    base_dir = os.path.dirname(csv_path)
    base_name = os.path.basename(csv_path)
    name, ext = os.path.splitext(base_name)
    output_csv = os.path.join(base_dir, f"{name}_통합헤더{ext}")

    # 매핑표 불러오기
    mapping_df = pd.read_csv(mapping_path, encoding='utf-8-sig')
    eng_to_kor = dict(zip(mapping_df.iloc[:, 1].astype(str).str.upper(),
                            mapping_df.iloc[:, 0].astype(str)))

    # 원본 CSV 읽기
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    new_columns = []

    for col in df.columns:
        parts = col.upper().split('_')              # 영문 약어 파싱
        kor_parts = [eng_to_kor.get(p, p) for p in parts]  # 한글 대응 치환
        kor_name = '_'.join(kor_parts)
        eng_name = '_'.join(parts)
        new_col = f"{kor_name}({eng_name})"
        new_columns.append(new_col)

    df.columns = new_columns
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"통합 헤더로 저장 완료 → {output_csv}")

if __name__ == "__main__":
    convert_headers_with_kor_augmented(
        csv_path=r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data\필터링데이터.csv",
        mapping_path=r"D:\workspace\project\KG_AI_Project\resource\csv_files\헤더약어매핑표.csv"
    )