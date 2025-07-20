import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import time
from Predictor.Controller import Controller

def main():
    print("[RUNNING] Predictor 파이프라인 시작")
    start_time = time.time()

    controller = Controller(config_name="Num01_Config_RFR.json")
    controller.run()

    end_time = time.time()
    print(f"\n[COMPLETE] 전체 예측 완료 → 소요 시간: {end_time - start_time:.2f}초")

if __name__ == "__main__":
    main()