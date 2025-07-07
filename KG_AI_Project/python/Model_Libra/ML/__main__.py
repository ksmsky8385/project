from OracleDBConnection import OracleDBConnection

def ConnectingDB():
    db = OracleDBConnection(
        username="libra",
        password="ksm0923",
        dsn="localhost:1521/XE",
        client_dir=r"C:\Users\user\Desktop\KSM\Tools\instantclient-basic-windows.x64-19.25.0.0.0dbru\instantclient_19_25"
        )

    db.connect()
    return db





if __name__ == "__main__":

    db = ConnectingDB()
    
    
    # db.close()