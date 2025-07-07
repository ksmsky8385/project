import pandas as pd

class NameMapper:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

        # 매핑 딕셔너리 (축약 예시, 실전에서는 풀버전 사용)
        self.mapping = {
        "Ajou University": "아주대학교",
        "Catholic Kwandong University": "가톨릭관동대학교",
        "Catholic University of Daegu": "대구가톨릭대학교",
        "Catholic University of Korea": "가톨릭대학교",
        "Cha University": "차의과학대학교",
        "Chonbuk National University": "전북대학교",
        "Chonnam National University": "전남대학교",
        "Chosun University": "조선대학교",
        "Chung-Ang University": "중앙대학교",
        "Chungbuk National University": "충북대학교",
        "Chungnam National University": "충남대학교",
        "Daegu Gyeongbuk Institute of Science and Technology": "대구경북과학기술원",
        "Daegu University": "대구대학교",
        "Dankook University": "단국대학교",
        "Dong-A University": "동아대학교",
        "Dongguk University": "동국대학교",
        "Eulji University": "을지대학교",
        "Ewha Womans University": "이화여자대학교",
        "Gachon University": "가천대학교",
        "Gangneung-Wonju National University": "국립강릉원주대학교",
        "Gwangju Institute of Science and Technology": "광주과학기술원",
        "Gyeongsang National University": "경상국립대학교",
        "Hallym University": "한림대학교",
        "Hanbat National University": "국립한밭대학교",
        "Hankuk University of Foreign Studies": "한국외국어대학교",
        "Hanyang University": "한양대학교",
        "Hongik University": "홍익대학교",
        "Incheon National University": "인천대학교",
        "Inha University": "인하대학교",
        "Inje University": "인제대학교",
        "Jeju National University": "제주대학교",
        "Jeonbuk National University": "전북대학교",
        "KAIST": "한국과학기술원",
        "Kangwon National University": "강원대학교",
        "Keimyung University": "계명대학교",
        "Kongju National University": "국립공주대학교",
        "Konkuk University": "건국대학교",
        "Kookmin University": "국민대학교",
        "Korea Advanced Institute of Science and Technology (KAIST)": "한국과학기술원",
        "Korea University": "고려대학교",
        "Kosin University": "고신대학교",
        "Kunsan National University": "국립군산대학교",
        "Kwangwoon University": "광운대학교",
        "Kyonggi University": "경기대학교",
        "Kyung Hee University": "경희대학교",
        "Kyungpook National University": "경북대학교",
        "Myongji University": "명지대학교",
        "Pohang University of Science and Technology": "포항공과대학교",
        "Pukyong National University": "국립부경대학교",
        "Pusan National University": "부산대학교",
        "Sejong University": "세종대학교",
        "Seoul National University": "서울대학교",
        "Seoul National University of Science and Technology": "서울과학기술대학교",
        "Sogang University": "서강대학교",
        "Sookmyung Women's University": "숙명여자대학교",
        "Soonchunhyang University": "순천향대학교",
        "Soongsil University": "숭실대학교",
        "Sunchon National University": "국립순천대학교",
        "Sungkyunkwan University": "성균관대학교",
        "Ulsan National Institute of Science and Technology": "울산과학기술원",
        "University of Science and Technology, Korea": "과학기술연합대학원대학교",
        "University of Seoul": "서울시립대학교",
        "University of Ulsan": "울산대학교",
        "Wonkwang University": "원광대학교",
        "Yeungnam University": "영남대학교",
        "Yonsei University": "연세대학교"
        }

    def run(self):
        
        try:
            df = pd.read_csv(self.input_path)
        except Exception as e:
            print(f"입력 파일 로딩 실패: {e}")
            return

        if "Institution" not in df.columns:
            print("'Institution' 컬럼이 없습니다.")
            return

        # 매핑 수행
        df["Korean_Name"] = df["Institution"].map(self.mapping)

        # 매핑 누락 항목 확인
        unmapped = df[df["Korean_Name"].isna()]
        if not unmapped.empty:
            print(f"매핑 실패 대학 수: {len(unmapped)}")
            print("다음 대학명은 매핑표에 없습니다:")
            for name in sorted(unmapped["Institution"].unique()):
                print(f"   - {name}")

        # 중복된 국문 대학명 검사
        dup_korean = df["Korean_Name"].value_counts()
        duplicated_korean = dup_korean[dup_korean > 1]
        if not duplicated_korean.empty:
            print(f"중복된 국문 대학명 수: {len(duplicated_korean)}")
            print("복수 영문명이 동일 국문으로 매핑됨:")
            for name, count in duplicated_korean.items():
                matched_eng = df[df["Korean_Name"] == name]["Institution"].unique()
                print(f"   - {name} ({count}건): {list(matched_eng)}")

        # 매핑 무결성 검사: 동일 영문 → 복수 국문 (이상 상황 탐지)
        mapping_df = df.dropna(subset=["Korean_Name"]).groupby("Institution")["Korean_Name"].nunique()
        invalid_mappings = mapping_df[mapping_df > 1]
        if not invalid_mappings.empty:
            print(f"매핑 오류: 하나의 영문명이 복수 국문으로 연결됨")
            for name in invalid_mappings.index:
                mapped_vals = df[df["Institution"] == name]["Korean_Name"].unique()
                print(f"   - {name} → {list(mapped_vals)}")

        # 저장
        df.to_csv(self.output_path, index=False, encoding="utf-8-sig")
        print(f"맵핑된 대학명 CSV 저장 완료: {self.output_path}")