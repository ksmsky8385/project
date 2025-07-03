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
        "2012년(A)": "2012A",
        "2013년(A)": "2013A",
        "2013년(B)": "2013B",
        "2014년(A)": "2014A",
        "2014년(B)": "2014B",
        "2014년(C)": "2014C",
        "2015년(A)": "2015A",
        "2015년(B)": "2015B",
        "2015년(C)": "2015C",
        "2016년(A)": "2016A",
        "2016년(B)": "2016B",
        "2016년(C)": "2016C",
        "2017년(A)": "2017A",
        "2017년(B)": "2017B",
        "2017년(C)": "2017C",
        "2018년(A)": "2018A",
        "2018년(B)": "2018B",
        "2018년(C)": "2018C",
        "2019년(A)": "2019A",
        "2019년(B)": "2019B",
        "2019년(C)": "2019C",
        "2020년(A)": "2020A",
        "2020년(B)": "2020B",
        "2020년(C)": "2020C",
        "2021년(A)": "2021A",
        "2021년(B)": "2021B",
        "2021년(C)": "2021C",
        "2022년(A)": "2022A",
        "2022년(B)": "2022B",
        "2022년(C)": "2022C",
        "2023년(B)": "2023B",
        "2023년(C)": "2023C",
        "2024년(C)": "2024C",
        "2급 정사서": "SL2",
        "[구독] e-Book": "SubEBook",
        "[구독] e-book": "SubEBook",
        "결산": "Settle",
        "겸직": "MultiRole",
        "계": "TotalSum",
        "교원": "Faculty",
        "교육 참가자수": "EduPartCnt",
        "교육 참여시간": "EduHours",
        "교육횟수": "EduCount",
        "구입": "Buy",
        "국내": "Domestic",
        "국내서": "DomBook",
        "국외": "Foreign",
        "국외서": "ForBook",
        "기증": "Donation",
        "기타": "Other",
        "기타 전자자료": "OthERes",
        "당해년도": "CurrYear",
        "대면 이용자 교육": "OnsiteEduUser",
        "대면교육": "OnsiteEdu",
        "대출자수": "LoanUserCnt",
        "대출책수": "LoanBookCnt",
        "대출현황": "LoanStatus",
        "대학규모": "UnivScale",
        "대학원생": "GradSt",
        "대학총결산": "UnivSettle",
        "대학총결산 대비 도서관 자료구입비 비율": "LibBgtRt",
        "대학총결산 대비 자료구입비 비율": "BgtRtSettle",
        "대학총예산": "UnivBgt",
        "도서관 이용자수": "LibUserCnt",
        "도서관건물연면적": "LibArea",
        "도서관건물연면적 (제곱미터)": "LibAreaSqm",
        "도서관직원수 비정규직": "LibStaffPT",
        "도서관직원수 정규직": "LibStaffFT",
        "도서자료": "BookRes",
        "도서자료 구입비": "BookCost",
        "동영상강의자료(e-Learning)": "ELearnVideo",
        "면담": "Consultation",
        "미소지자": "NoHolder",
        "방문자수": "VisitCnt",
        "번호": "ID",
        "봉사대상자수": "VolunteerTC",
        "봉사대상자수 및 이용자수": "VolunteerUserCnt",
        "비대면 실시간 교육": "RemoteEduLive",
        "비대면 이용자 교육": "RemoteEduUser",
        "비도서자료 구입비": "NonBookCost",
        "비사서": "NonLibrarian",
        "비전임교원": "PartFaculty",
        "비정규직": "PartTime",
        "사서": "Librarian",
        "사서자격증 미소지자": "NoCertLibrarian",
        "사서자격증 보유현황": "LibrarianCertStat",
        "사서자격증 소지자": "HasCertLibrarian",
        "사서직원수 비정규직": "LibraPT",
        "사서직원수 정규직": "LibraFT",
        "상호대차 신청 및 제공 건수": "RefLoan",
        "설립": "FoundType",
        "설비": "Equip",
        "소장도서수": "BooksOwned",
        "시설": "Facility",
        "신청": "Request",
        "업무용컴퓨터(PC)수": "StaffPCs",
        "연간 장서 증가 및 폐기 책수": "AnnualHoldChg",
        "연간 장서 증가 종수": "AnnualTitleInc",
        "연간 장서 증가 책수": "AnnualBookInc",
        "연간 장서 폐기 책수": "AnnualBookRm",
        "연간장서증가율": "HoldGrowRate",
        "연간장서증가책수": "AnnualHoldBookCount",
        "연도": "Year",
        "연면적": "Area",
        "연속간행물": "Serials",
        "연속간행물 구입비": "SerialsCost",
        "열람석": "ReadSeat",
        "예산": "Budget",
        "온라인": "Online",
        "온라인 교육": "OnlineEdu",
        "원문복사 신청 및 제공 건수": "RefCopy",
        "웹DB": "WebDB",
        "이용자 교육": "UserEdu",
        "이용자수": "UserCnt",
        "이용자용컴퓨터(PC)수": "UserPCs",
        "자료구입비": "MatCost",
        "자료구입비(결산)": "MatCostSettle",
        "자료구입비계": "MatCostTot",
        "재학생 1,000명당 도서관 직원수": "StaffPerKSt",
        "재학생 1,000명당 사서 직원수": "LibrarianPerKSt",
        "재학생 1인당 도서관건물 연면적": "AreaPerSt",
        "재학생 1인당 도서관방문자수": "VisitPerSt",
        "재학생 1인당 대출책수": "LoanPerSt",
        "재학생 1인당 소장도서수": "BooksPerSt",
        "재학생 1인당 자료구입비": "CostPerSt",
        "재학생 1인당 자료구입비(결산)": "CostPerStSettle",
        "재학생수": "StCount",
        "재학생수(당해년도)": "StCountCurr",
        "재학생수(전년도)": "StCountPrev",
        "전년도": "PrevYear",
        "전담": "Exclusive",
        "전임교원": "FullFaculty",
        "전자자료": "ERes",
        "전자자료 구입비": "ECost",
        "전자저널": "EJournal",
        "전화": "Phone",
        "정규직": "FullTime",
        "정보화기기(PC)수": "InfoPCs",
        "제공": "Provided",
        "종수": "TitleCount",
        "준사서": "AsstLibrarian",
        "지역": "Region",
        "직원": "Staff",
        "직원 1인당 평균 교육 참여 시간": "EduHrsPerStaff",
        "직원교육현황": "StaffEducationStatus",
        "참고서비스 및 상호협력": "RefCollab",
        "참고서비스 신청 및 제공 건수 (2010년 이전)": "RefBefore2010",
        "참고서비스 제공 건수 (2010년 이후)": "RefAfter2010",
        "참여시간": "PartiHrs",
        "참여인원": "PartiCnt",
        "책수": "BookCount",
        "총 보유컴퓨터(PC)수": "TotalPCs",
        "총열람석수": "TotSeats",
        "최근 3년간 자료구입비 증가율(결산)": "BgtGrowth3Y",
        "패키지": "Package",
        "학과수": "DeptCnt",
        "학교명": "SchName",
        "학교유형": "SchType",
        "학부생": "Undergrad",
        "합계": "Total"
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