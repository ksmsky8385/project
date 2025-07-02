from ExcelToCSVConverter_ver1 import ExcelToCSVConverter_ver1
from ExcelToCSVConverter_ver2 import ExcelToCSVConverter_ver2
from CSVToOracleUploader import CSVToOracleUploader
from HeaderTermCollector import HeaderTermCollector


if __name__ == "__main__":

    def ExcelToCSV_ver1():

        target = [
            ("기본통계_소장및구독자료.xlsx", "Num01_소장및구독자료"),
            ("기본통계_예산및결산.xlsx", "Num03_예산및결산"),
            ("기본통계_이용및이용자.xlsx", "Num04_이용및이용자"),
            ("기본통계_인적자원.xlsx", "Num05_인적자원")
        ]

        save_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files"

        for filename, prefix in target:
            path = rf"D:\workspace\project\KG_AI_Project\resource\raw_files\{filename}"
            converter = ExcelToCSVConverter_ver1(file_path=path, output_prefix=prefix, save_dir=save_dir)
            converter.run()

        print('\n📦 모든 파일 변환 완료.\n')
        
    def ExcelToCSV_ver2() :
        target = [
            ("기본통계_시설.xlsx", "Num02_시설"),
        ]

        save_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files"

        for filename, prefix in target:
            path = rf"D:\workspace\project\KG_AI_Project\resource\raw_files\{filename}"
            converter = ExcelToCSVConverter_ver2(file_path=path, output_prefix=prefix, save_dir=save_dir)
            converter.run()
            
        print('\n📦 모든 파일 변환 완료.\n')

    def HeaderCollellector():
        csv_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files"
        save_path = r"D:\workspace\project\KG_AI_Project\resource\모든헤더목록.txt"

        collector = HeaderTermCollector(csv_dir=csv_dir)
        collector.run()
        collector.save_terms(path=save_path)






    def createDB():
        username = "libra"
        password = "ksm0923"
        dsn = "localhost:1521/XE"
        csv_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files"
        client_dir = r"C:\\Users\\user\\Desktop\\KSM\\Tools\\instantclient-basic-windows.x64-19.25.0.0.0dbru\\instantclient_19_25"

        loader = CSVToOracleUploader(username, password, dsn, csv_dir, client_dir)
        loader.run()

        print('\nDB 생성 완료.\n')



    # ExcelToCSV_ver1()
    # ExcelToCSV_ver2()
    HeaderCollellector()
    # createDB()