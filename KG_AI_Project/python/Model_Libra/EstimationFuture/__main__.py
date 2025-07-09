import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from EstimationFuture.ModelLoader import ModelLoader
from EstimationFuture.SCRTableBuilder import SCRTableBuilder
from EstimationFuture.SCRTableUpdater import SCRTableUpdater

if __name__ == "__main__":
    model_loader = ModelLoader()
    
    builder = SCRTableBuilder(model_loader=model_loader)
    builder.build_table()
    
    updater = SCRTableUpdater(model_loader)

    bound = 1  # 필요 예측 추가 횟수 설정 (0이면 실행되지 않음)

    if bound > 0:
        for _ in range(bound):
            updater.update_table()
    else:
        print("[업데이트 생략] bound 값이 0이라 추가 예측은 수행하지 않습니다.")
