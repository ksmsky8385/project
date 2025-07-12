import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ML_RFR.controller import RFRPipelineController
from core_utiles.config_loader import (ORACLE_CLIENT_PATH, RFR_SAVE_PATH)
from core_utiles.OracleDBConnection import OracleDBConnection

if __name__ == "__main__":
    db = OracleDBConnection()
    db.connect()

    controller = RFRPipelineController(conn=db.conn, oracle_client_path=ORACLE_CLIENT_PATH, rfr_save_path=RFR_SAVE_PATH)
    controller.setup_oracle_client()
    controller.run()

    db.close()
