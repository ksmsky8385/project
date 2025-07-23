import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tunercontroller_Num01 import TunerController_Num01
from tunercontroller_Num02 import TunerController_Num02
from Tuner.extractor_Num01 import Num01Extractor

def main():
    config_name = os.getenv("MODEL_CONFIG_NAME", "Num02_Config_XGB.json")
    config_path = Path(__file__).resolve().parent.parent / "_Configs" / config_name
    log_dir = Path(__file__).resolve().parent.parent / "_Logs" / "Tuner_Logs"
    log_dir.mkdir(exist_ok=True, parents=True)

    trial_count = 10
    rating_cycle = 5

    if "Num01" in config_name:
        controller = TunerController_Num01(config_path, log_dir, trial_count, rating_cycle)
    elif "Num02" in config_name:
        controller = TunerController_Num02(config_path, log_dir, trial_count, rating_cycle)
    else:
        raise ValueError(f"[ERROR] 지원하지 않는 모델 번호: {config_name}")

    controller.run()

def extraction_num01():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(base_dir, "..", "_Logs", "Tuner_Logs", "Num01_Tuner_Log_20250721_213441.json")
    extractor = Num01Extractor(log_path)
    extractor.extract_top_n(n=5)


if __name__ == "__main__":
    # main()
    extraction_num01()
