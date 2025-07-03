import os
import csv

class HeaderAbbreviationMapper:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path     # 한글 헤더 텍스트 또는 CSV 경로
        self.output_path = output_path   # 매핑 테이블 저장 경로
        self.original_headers = set()
        self.mapping = {}

    def load_headers(self):
        ext = os.path.splitext(self.input_path)[-1].lower()
        if ext == ".txt":
            with open(self.input_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.original_headers.add(line)
        elif ext == ".csv":
            with open(self.input_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                if "한글헤더" not in reader.fieldnames:
                    raise ValueError("CSV 파일에 '한글헤더' 컬럼이 존재하지 않습니다.")
                for row in reader:
                    value = row["한글헤더"].strip()
                    if value:
                        self.original_headers.add(value)

        else:
            raise ValueError("지원되지 않는 입력 파일 형식입니다 (.txt 또는 .csv만 가능)")

    def generate_abbreviations(self):
        for h in sorted(self.original_headers):
            abbr = self.rule_based_abbreviation(h)
            self.mapping[h] = abbr

    def rule_based_abbreviation(self, text: str) -> str:
        replace_dict = {
        "1급 정사서": "SL1",
        "2012년(A)": "12A",
        "2013년(A)": "13A",
        "2013년(B)": "13B",
        "2014년(A)": "14A",
        "2014년(B)": "14B",
        "2014년(C)": "14C",
        "2015년(A)": "15A",
        "2015년(B)": "15B",
        "2015년(C)": "15C",
        "2016년(A)": "16A",
        "2016년(B)": "16B",
        "2016년(C)": "16C",
        "2017년(A)": "17A",
        "2017년(B)": "17B",
        "2017년(C)": "17C",
        "2018년(A)": "18A",
        "2018년(B)": "18B",
        "2018년(C)": "18C",
        "2019년(A)": "19A",
        "2019년(B)": "19B",
        "2019년(C)": "19C",
        "2020년(A)": "20A",
        "2020년(B)": "20B",
        "2020년(C)": "20C",
        "2021년(A)": "21A",
        "2021년(B)": "21B",
        "2021년(C)": "21C",
        "2022년(A)": "22A",
        "2022년(B)": "22B",
        "2022년(C)": "22C",
        "2023년(B)": "23B",
        "2023년(C)": "23C",
        "2024년(C)": "24C",
        "2급 정사서": "SL2",
        "[구독] e-Book": "EB",
        "[구독] e-book": "EB",
        "결산": "STL",
        "겸직": "MRL",
        "계": "SUM",
        "교원": "FAC",
        "교육 참가자수": "EP",
        "교육 참여시간": "EH",
        "교육횟수": "EDC",
        "구입": "BUY",
        "국내": "KR",
        "국내서": "KB",
        "국외": "OT",
        "국외서": "OB",
        "기증": "DON",
        "기타": "OTH",
        "기타 전자자료": "OER",
        "당해년도": "CYR",
        "대면 이용자 교육": "OEU",
        "대면교육": "OE",
        "대출자수": "LU",
        "대출책수": "LB",
        "대출현황": "LS",
        "대학규모": "USC",
        "대학원생": "GRAD",
        "대학총결산": "USTL",
        "대학총결산 대비 도서관 자료구입비 비율": "LBRT",
        "대학총결산 대비 자료구입비 비율": "BRT",
        "대학총예산": "UBGT",
        "도서관 이용자수": "LUC",
        "도서관건물연면적": "LA",
        "도서관건물연면적 (제곱미터)": "LAS",
        "도서관직원수 비정규직": "LPT",
        "도서관직원수 정규직": "LFT",
        "도서자료": "BR",
        "도서자료 구입비": "BC",
        "동영상강의자료(e-Learning)": "ELV",
        "면담": "CSLT",
        "미소지자": "NOH",
        "방문자수": "VC",
        "번호": "ID",
        "봉사대상자수": "VTC",
        "봉사대상자수 및 이용자수": "VUC",
        "비대면 실시간 교육": "REL",
        "비대면 이용자 교육": "REU",
        "비도서자료 구입비": "NBC",
        "비사서": "NLIB",
        "비전임교원": "PFAC",
        "비정규직": "PT",
        "사서": "LIB",
        "사서자격증 미소지자": "NLIBC",
        "사서자격증 보유현황": "LIBCS",
        "사서자격증 소지자": "HLIBC",
        "사서직원수 비정규직": "LPT2",
        "사서직원수 정규직": "LFT2",
        "상호대차 신청 및 제공 건수": "RFLN",
        "설립": "FND",
        "설비": "EQP",
        "소장도서수": "BO",
        "순위": "RK",
        "시설": "FACLT",
        "신청": "REQ",
        "업무용컴퓨터(PC)수": "SPC",
        "연간 장서 증가 및 폐기 책수": "AHC",
        "연간 장서 증가 종수": "ATI",
        "연간 장서 증가 책수": "ABI",
        "연간 장서 폐기 책수": "ARM",
        "연간장서증가율": "GRR",
        "연간장서증가책수": "AHBC",
        "연도": "YR",
        "연면적": "AR",
        "연속간행물": "SRL",
        "연속간행물 구입비": "SRC",
        "열람석": "RS",
        "예산": "BGT",
        "온라인": "ONL",
        "온라인 교육": "OE2",
        "원문복사 신청 및 제공 건수": "RFC",
        "웹DB": "WDB",
        "이용자 교육": "UE",
        "이용자수": "UC",
        "이용자용컴퓨터(PC)수": "UPC",
        "자료구입비": "MC",
        "자료구입비(결산)": "MCS",
        "자료구입비계": "MCT",
        "재학생 1,000명당 도서관 직원수": "SPK",
        "재학생 1,000명당 사서 직원수": "LPK",
        "재학생 1인당 도서관건물 연면적": "APS",
        "재학생 1인당 도서관방문자수": "VPS",
        "재학생 1인당 대출책수": "LPS",
        "재학생 1인당 소장도서수": "BPS",
        "재학생 1인당 자료구입비": "CPS",
        "재학생 1인당 자료구입비(결산)": "CPSS",
        "재학생수": "SC",
        "재학생수(당해년도)": "SCC",
        "재학생수(전년도)": "SCP",
        "전년도": "PYR",
        "전담": "EXC",
        "전임교원": "FFAC",
        "전자자료": "ER",
        "전자자료 구입비": "ERC",
        "전자저널": "EJN",
        "전화": "PHN",
        "점수": "SCR",
        "정규직": "FT",
        "정보화기기(PC)수": "TPC",
        "제공": "PRV",
        "종수": "TCNT",
        "준사서": "ALIB",
        "지역": "RGN",
        "직원": "STF",
        "직원 1인당 평균 교육 참여 시간": "EHS",
        "직원교육현황": "SES",
        "참고서비스 및 상호협력": "RCOL",
        "참고서비스 신청 및 제공 건수 (2010년 이전)": "RBF10",
        "참고서비스 제공 건수 (2010년 이후)": "RAF10",
        "참여시간": "PTH",
        "참여인원": "PTC",
        "책수": "BCNT",
        "총 보유컴퓨터(PC)수": "TPC",
        "총열람석수": "TRS",
        "최근 3년간 자료구입비 증가율(결산)": "BG3Y",
        "패키지": "PKG",
        "학과수": "DPC",
        "학교명": "SNM",
        "학교유형": "STYP",
        "학부생": "UGRD",
        "합계": "TTL"
        }

        return replace_dict.get(text, text)

    def save_mapping_csv(self):
        with open(self.output_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["한글헤더", "영문약어"])

            # ✅ 원본 헤더 순서대로, 정확 일치하는 key만 매핑
            for original in sorted(self.original_headers):
                # rule_based_abbreviation을 직접 호출해서 매핑 수행
                english = self.rule_based_abbreviation(original)
                writer.writerow([original, english])
                if original == english:
                    print(f"⚠️ 매핑 없음: {original}")
        
        print(f"📂 저장경로 : {self.output_path}")
        print(f"💾 영문 약어 매핑 CSV 저장 완료")

    def check_duplicate_abbreviations_from_file(self):
        duplicates = {}
        seen = {}

        try:
            with open(self.output_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    korean = row["한글헤더"].strip()
                    english = row["영문약어"].strip()

                    if english in seen:
                        duplicates.setdefault(english, set()).update([korean, seen[english]])
                    else:
                        seen[english] = korean

            if duplicates:
                print("\n❗ 중복된 영문약어 발견:")
                for abbr, headers in duplicates.items():
                    print(f"  - {abbr} ← {sorted(headers)}")
            else:
                print("✅ 모든 영문약어가 유일합니다.")

            print("✅ 영문약어 무결성 검사 완료.")

        except Exception as e:
            print(f"❌ 무결성 검사 중 오류 발생: {e}")
        
    def run(self):
        self.load_headers()
        self.generate_abbreviations()
        self.save_mapping_csv()
        self.check_duplicate_abbreviations_from_file() 