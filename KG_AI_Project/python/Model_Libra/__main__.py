import subprocess
import sys
import os
from dotenv import load_dotenv, find_dotenv

# 현재 스크립트 경로 기준으로 Model_Libra 디렉터리를 path에 추가
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "."))  # Model_Libra 폴더 기준

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


print("Model_Libra 실행 시작")

# .env 파일 로딩 체크
env_path = find_dotenv()
if not env_path:
    print(".env 파일을 찾을 수 없습니다. 환경설정을 먼저 확인해주세요.")
else:
    load_dotenv(env_path)
    print(f".env 파일 로딩 완료 → {env_path}")

# 실행 대상 패키지 정의
execution_order = [
    "DataHandling",
    "DBHandling",
    "ML_RFR",
    "EstimationFlow",
    "ML_XGB",
    "EstimationFuture"
]

# 실행 루프
for package in execution_order:
    package_path = os.path.join(PROJECT_ROOT, package)
    main_path = os.path.join(package_path, "__main__.py")

    # 패키지 폴더 존재 여부 체크
    if not os.path.isdir(package_path):
        print(f"패키지 폴더 없음 ➜ {package_path}")
        break

    # __main__.py 존재 여부 체크
    if not os.path.isfile(main_path):
        print(f"실행 파일 없음 ➜ {main_path}")
        break

    print(f"\n실행 중: {package}/__main__.py")

    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT
    result = subprocess.run(
                            [sys.executable, main_path],
                            env=env,
                            capture_output=True,
                            text=True
                            )


    print(result.stdout)

    if result.returncode != 0:
        print(f"{package} 실행 실패: {result.stderr}")
        break
else:
    print("\n전체 파이프라인 완료!")