from OracleDBConnection import OracleDBConnection
from TableMergerUploader import TableMergerUploader
from DataMergerAndExporter import DataMergerAndExporter
from FilteredScoreUploader import FilteredScoreUploader

def ConnectingDB():
    db = OracleDBConnection(
        username="libra",
        password="ksm0923",
        dsn="localhost:1521/XE",
        client_dir=r"C:\Users\user\Desktop\KSM\Tools\instantclient-basic-windows.x64-19.25.0.0.0dbru\instantclient_19_25"
        )

    db.connect()
    return db

def TableMerge(db):
    common_columns = ['YR', 'ID', 'SNM', 'STYP', 'FND', 'RGN', 'USC']
    years = range(2014, 2025)

    csv_prefix = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data\Num06_종합데이터"  # 저장 파일 이름 접두사
    table_prefix = "NUM06"  # 테이블 이름 접두사

    uploader = TableMergerUploader(
        conn=db.conn,
        cursor=db.cursor,
        years=years,
        common_cols=common_columns,
        csv_prefix=csv_prefix,
        table_prefix=table_prefix
    )
    uploader.process_all_years()

def ScoreTableData(db):
    file_prefix = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data\Num07_평가대학데이터"  # 저장 파일 이름 접두사
    table_prefix = "NUM07"  # 테이블 이름 접두사
    years = range(2014, 2025)
    merger = DataMergerAndExporter(
    conn=db.conn,
    cursor=db.cursor,
    years=years,
    file_prefix=file_prefix,
    table_prefix=table_prefix
    )
    merger.merge_and_save()

def ScoreFilteredData(db):
    years = range(2014, 2025)
    csv_prefix = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data\필터링데이터"
    table_name = "FILTERED"

    input_abbr = [
        'BCNT_SUM', 'BPS', 'ABI', 'LAS', 'TRS', 'TPC', 'APS',
        'UBGT', 'USTL', 'MCT', 'CPS',
        'LUC', 'LU_SUM', 'LB_SUM', 'EDC', 'EP', 'LPS', 'VPS',
        'SPK', 'LPK', 'EHS'
    ]

    uploader = FilteredScoreUploader(
        conn=db.conn,
        cursor=db.cursor,
        years=years,
        input_abbr=input_abbr,
        csv_prefix=csv_prefix,
        table_name=table_name
    )
    uploader.run()





if __name__ == "__main__":

    db = ConnectingDB()

    TableMerge(db)
    ScoreTableData(db)
    ScoreFilteredData(db)

    # db.close()