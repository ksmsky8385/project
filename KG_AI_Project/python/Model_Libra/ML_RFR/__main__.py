import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ML_RFR.controller import RFRPipelineController
from core_utiles.config_loader import (ORACLE_CLIENT_PATH, RFR_SAVE_PATH)
from core_utiles.OracleDBConnection import OracleDBConnection

if __name__ == "__main__":
    db = OracleDBConnection()
    db.connect()

    controller = RFRPipelineController(conn=db.conn, oracle_client_path=ORACLE_CLIENT_PATH, rfr_save_path=RFR_SAVE_PATH)
    controller.setup_oracle_client()
    
    results = controller.run()

    log_path = os.path.join(RFR_SAVE_PATH, "metrics_log.json")
    log_dict = {
        "full_model": results["full_model"],
        "cluster_test": results["cluster_test"],
        "full_predict": results["full_predict"]
    }

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_dict, f, indent=2, ensure_ascii=False)


    print("[로그 생성 완료] → metrics_log.json")
    print(f"Log save path: {log_path}")
    print(f"Save dir exists? → {os.path.exists(RFR_SAVE_PATH)}")
    db.close()
