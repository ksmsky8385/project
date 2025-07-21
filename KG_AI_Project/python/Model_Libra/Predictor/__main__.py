import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Predictor.Controller import Controller

def main():
    print("[RUNNING] Predictor 파이프라인 시작")
    start_time = time.time()

    config_name = os.getenv("MODEL_CONFIG_NAME", "Num01_Config_RFR.json")
    controller = Controller(config_name=config_name)
    controller.run()

    print(f"[COMPLETE] 소요 시간: {time.time() - start_time:.2f}초")

if __name__ == "__main__":
    main()
