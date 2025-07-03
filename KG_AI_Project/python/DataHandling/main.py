from ExcelToCSVConverter_ver1 import ExcelToCSVConverter_ver1
from ExcelToCSVConverter_ver2 import ExcelToCSVConverter_ver2
from CWURCrawler import CWURCrawler
from EnNameCollector import EnNameCollector
from NameMapper import NameMapper
from RankedScoreExporter import RankedScoreExporter
from HeaderTermCollector import HeaderTermCollector
from HeaderAbbreviationMapper import HeaderAbbreviationMapper
from CSVHeaderRenamer import CSVHeaderRenamer
from CSVToOracleUploader import CSVToOracleUploader

if __name__ == "__main__":

    # 대학도서관 데이터 xlsx파일 csv 파일로 변환 _ 기본형
    def ExcelToCSV_ver1():
        print("\n🛠️   원본데이터 CSV로 변환_Ver1 시작\n")
        target = [
            ("기본통계_소장및구독자료.xlsx", "Num01_소장및구독자료"),
            ("기본통계_예산및결산.xlsx", "Num03_예산및결산"),
            ("기본통계_이용및이용자.xlsx", "Num04_이용및이용자"),
            ("기본통계_인적자원.xlsx", "Num05_인적자원")
        ]

        save_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"

        for filename, prefix in target:
            path = rf"D:\workspace\project\KG_AI_Project\resource\raw_files\{filename}"
            converter = ExcelToCSVConverter_ver1(file_path=path, output_prefix=prefix, save_dir=save_dir)
            converter.run()

        print('\n📦  모든 파일 변환 완료.\n')

    # 대학도서관 데이터 xlsx파일 csv 파일로 변환 _ 특이형 파일 전용
    def ExcelToCSV_ver2() :
        print("\n🛠️  원본데이터 CSV로 변환_Ver2 시작\n")
        target = [
            ("기본통계_시설.xlsx", "Num02_시설"),
        ]

        save_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"

        for filename, prefix in target:
            path = rf"D:\workspace\project\KG_AI_Project\resource\raw_files\{filename}"
            converter = ExcelToCSVConverter_ver2(file_path=path, output_prefix=prefix, save_dir=save_dir)
            converter.run()
            
        print('\n📦  모든 파일 변환 완료.\n')

    # CWUR 사이트에서 상위 한국대학 평가점수 크롤링
    def Crawling():
        print("\n🛠️  CWUR사이트 대학평가점수 크롤링 시작\n")
        folder_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"
        output_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\대학평가점수크롤링.csv"

        crawler = CWURCrawler(folder_path, output_path)
        crawler.run()

    # 크롤링 데이터의 영문 대학명 리스트 생성
    def EnNameList():
        print("\n🛠️  대학 영문명 리스트화 시작\n")
        input_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\대학평가점수크롤링.csv"
        output_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\대학영문명리스트.csv"

        extractor = EnNameCollector(input_path, output_path)
        extractor.run()

    # 영문 대학명 한국명으로 매핑파일 생성
    def NameMapping():
        print("\n🛠️  영문명 매핑 시작\n")
        input_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\대학영문명리스트.csv"
        output_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\대학명매핑표.csv"

        mapper = NameMapper(input_path, output_path)
        mapper.run()
        
    #매핑파일 기반 연도별 대학평가점수 csv파일 생성
    def ScoreCSVExporter():
        score_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\대학평가점수크롤링.csv"
        mapping_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\대학명매핑표.csv"
        output_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"

        exporter = RankedScoreExporter(score_path, mapping_path, output_dir)
        exporter.run()

    # 모든 csv 변환 파일 각각의 컬럼명에 존재하는 헤더 수집
    def HeaderCollellector():
        print("\n🛠️  헤더 수집 시작\n")
        
        csv_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"
        save_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\모든헤더목록표.csv"

        collector = HeaderTermCollector(csv_dir=csv_dir)
        collector.run()
        collector.save_terms(path=save_path)

    # 수집된 헤더명을 영어 약문으로 변환 매칭작업
    def HeaderMapper():
        print("\n🛠️  헤더 매핑 시작\n")
        input_header_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\모든헤더목록표.csv"
        output_mapping_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\헤더약어매핑표.csv"

        mapper = HeaderAbbreviationMapper(input_path=input_header_path, output_path=output_mapping_path)
        mapper.run()

    # 모든 csv파일의 컬럼명에 있는 헤더명을 모두 영어약문으로 변경 후 저장
    def HeaderRenamer():
        print("\n🛠️  csv파일 컬럼명 변경 작업 시작\n")
        csv_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"
        mapping_csv = r"D:\workspace\project\KG_AI_Project\resource\csv_files\헤더약어매핑표.csv"

        renamer = CSVHeaderRenamer(csv_folder=csv_dir, mapping_path=mapping_csv)
        renamer.process_all_csvs()

    # 모든 csv파일 오라클DB에 테이블로 저장
    def CreateDB():
        print("\n🛠️  Oracl DB 테이블 생성 시작\n")
        username = "libra"
        password = "ksm0923"
        dsn = "localhost:1521/XE"
        csv_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"
        client_dir = r"C:\\Users\\user\\Desktop\\KSM\\Tools\\instantclient-basic-windows.x64-19.25.0.0.0dbru\\instantclient_19_25"

        loader = CSVToOracleUploader(username, password, dsn, csv_dir, client_dir)
        loader.run()

        print('\n📦  DB 생성 완료.\n')

    # 메서드 실행

    # ExcelToCSV_ver1()
    # ExcelToCSV_ver2()
    # Crawling()
    # EnNameList()
    # NameMapping()
    # ScoreCSVExporter()
    # HeaderCollellector()
    # HeaderMapper()
    # HeaderRenamer()
    CreateDB()