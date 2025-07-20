import os
import sys
import time

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ModelCreator.Controller import PipelineController

def main():
    print("[RUNNING] ModelCreator 파이프라인 시작")
    start_time = time.time()

    config_path = os.path.join(os.path.dirname(__file__), "..", "_Configs", "Num01_Config_RFR.json")

    controller = PipelineController(config_path=config_path)
    controller.run()

    end_time = time.time()
    print(f"\n[COMPLETE] 전체 파이프라인 완료 → 소요 시간: {end_time - start_time:.2f}초")

if __name__ == "__main__":
    main()