# Tuner_RFR/__main__.py

import sys, os
from pathlib import Path
import json

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tunercontroller import TunerController
from tunerlogranker import TunerLogRanker

if __name__ == "__main__":
    # 현재 파일 기준 디렉토리
    tuner_dir = Path(__file__).parent
    log_path = tuner_dir / "tuner_log.json"
    output_path = tuner_dir / "toprating.json"

    # 로그 파일 초기화
    for path in [log_path, output_path]:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

    # 튜닝 수행
    controller = TunerController(n_trials=1000)
    controller.run()

    # 랭킹 추출
    ranker = TunerLogRanker(
        log_path=log_path,
        output_path=output_path
    )
    ranker.rank_top_trials(top_k=10)
