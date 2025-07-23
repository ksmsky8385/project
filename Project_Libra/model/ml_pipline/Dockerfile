# 1. 베이스 이미지 선택 (파이썬 사용)
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 프로젝트 파일들을 컨테이너로 복사
COPY . /app

# 4. 의존성 설치 (requirements.txt 기반)
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 5. 실행 명령 설정 (패키지 진입점이 __main__.py라고 가정)
CMD ["python", "__main__.py"]
