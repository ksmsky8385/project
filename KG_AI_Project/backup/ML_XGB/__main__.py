import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ML_XGB.controller import XGBPipelineController

if __name__ == "__main__":
    controller = XGBPipelineController()
    controller.run()
