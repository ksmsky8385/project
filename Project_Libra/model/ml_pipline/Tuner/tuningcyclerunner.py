import os
import subprocess
from pathlib import Path

def run_modelcreator(config_obj):
    config_path = config_obj.config_path
    os.environ["MODEL_CONFIG_NAME"] = config_path.name

    # 프로젝트 루트에서 ModelCreator 위치 설정
    project_root = Path(__file__).resolve().parent.parent
    modelcreator_main = project_root / "ModelCreator" / "__main__.py"

    subprocess.run(
        ["python", str(modelcreator_main)],
        check=True
    )

def run_predictor(config_obj):
    config_path = config_obj.config_path
    os.environ["MODEL_CONFIG_NAME"] = config_path.name

    project_root = Path(__file__).resolve().parent.parent
    predictor_main = project_root / "Predictor" / "__main__.py"

    subprocess.run(["python", str(predictor_main)], check=True)
