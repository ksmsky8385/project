from ExcelToCSVConverter_ver1 import ExcelToCSVConverter_ver1
from ExcelToCSVConverter_ver2 import ExcelToCSVConverter_ver2
from CSVToDB import CSVToDB

if __name__ == "__main__":

    save_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files"

    def ver1() :
        target = [
            ("기본통계_소장및구독자료.xlsx", "Num01_소장및구독자료"),
            ("기본통계_예산및결산.xlsx", "Num03_예산및결산"),
            ("기본통계_이용및이용자.xlsx", "Num04_이용및이용자"),
            ("기본통계_인적자원.xlsx", "Num05_인적자원")
        ]

        for filename, prefix in target:
            path = rf"D:\workspace\project\KG_AI_Project\resource\raw_files\{filename}"
            converter = ExcelToCSVConverter_ver1(file_path=path, output_prefix=prefix, save_dir=save_dir)
            converter.run()
            
        print('\n모든 파일 변환 완료.\n')
        
    def ver2() :
        target = [
            ("기본통계_시설.xlsx", "Num02_시설"),
        ]

        for filename, prefix in target:
            path = rf"D:\workspace\project\KG_AI_Project\resource\raw_files\{filename}"
            converter = ExcelToCSVConverter_ver2(file_path=path, output_prefix=prefix, save_dir=save_dir)
            converter.run()
            
        print('\n모든 파일 변환 완료.\n')
    
    def createDB():
        csv_loader = CSVToDB(
            username='libra',
            password='ksm0923',
            dsn='Libra_DB',
            csv_dir=r'D:\workspace\project\KG_AI_Project\resource\csv_files'
        )
        csv_loader.run()
        
        print('\nDB 생성 완료.\n')

    
    
    
    # ver1()
    # ver2()
    createDB()