import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from EstimationFuture.ModelLoader import ModelLoader
from EstimationFuture.SCRTableBuilder import SCRTableBuilder

if __name__ == "__main__":
    model_loader = ModelLoader()
    builder = SCRTableBuilder(model_loader=model_loader)
    builder.build_table()
