# 파이썬 프로젝트 패키지 구성

### 00. 디렉토리 구성 및 설명

Model_Libra/
│
├── core_utiles/ <- 공통 모듈 전용 폴더
│   ├── __init__.py
│   ├── config_loader.py <- .env 로드 모듈
│   ├── HeaderConvorter.py <- 전처리 데이터 컬럼 한영 변환툴
│   ├── HeaderRemaker.py <- 전처리 데이터 컬럼 가독성 보완툴
│   ├── OracleDBConnection.py <- 오라클DB 접속 모듈
│   ├── OracleSchemaBuilder.py <- 테이블 생성 시 데이터타입 보정 모듈
│   └── OracleTableCreater.py <- 데이터타입 보정 후 테이블 생성 모듈
│
├── DataHandling/ <- 원본파일 CSV파일화 및 DB 업로드 패키지
│   ├── __init__.py
│   ├── __main__.py <- DataHandling 패키지 실행
│   ├── (09) CSVHeaderRenamer.py <- 모든 csv파일 컬럼 별 헤더 영문약어로 변경 클래스
│   ├── (10) CSVToOracleUploader.py <- 오라클DB로 모든 csv파일 테이블 생성 클래스
│   ├── (03) CWURCrawler.py <- CWUR 사이트 대학 평가점수 크롤링 클래스
│   ├── (04) EnNameCollector.py <- 크롤링 데이터 영문 대학명 리스트화 클래스
│   ├── (01) ExcelToCSVConverter_ver1.py <- CSV파일 변환 클래스 1
│   ├── (02) ExcelToCSVConverter_ver2.py <- CSV파일 변환 클래스 2
│   ├── (08) HeaderAbbreviationMapper.py <- 헤더 한글 영문 매핑 클래스
│   ├── (07) HeaderTermCollector.py <- 모든 csv파일 컬럼 별 헤더 수집 클래스
│   ├── (05) NameMapper.py <- 영문 대학명 한국명으로 매핑 클래스
│   └── (06) RankedScoreExporter.py <- 연도 별 대학 평가점수 csv 파일 생성
│
├── DBHandling/ <- 생성된 DB테이블 기반 전처리 및 정규화 패키지
│   ├── __init__.py
│   ├── __main__.py <- DBHandling 패키지 실행
│   ├── (02) DataMergerAndExporter.py <- 평가점수 + 대학 별 데이터 병합 및 테이블 생성 클래스
│   ├── (03) FilteredScoreUploader.py <- 인풋 & 타깃 컬럼 정규화 테이블 생성 클래스
│   └── (01) TableMergerUploader.py <- 모든 데이터테이블 연도별로 병합 및 테이블 생성 클래스
│
├── ML/ <- 머신러닝 작동 패키지
│   ├── __init__.py
│   ├── __main__.py <- ML 패키지 실행
│   └── trainer.py
│
├── __init__.py
├── __main__.py <- Model_Libra 내부 패키지 전체 실행
├── .env.template <- 계정 및 패스 설정
├── environment.yml <- " conda env create -f environment.yml " 아나콘다 가상환경 세팅
├── README.md <- 설명글
└── requirements.txt <- " pip install -r requirements.txt " 필요 라이브러리 설치



### 01. 환경세팅

두가지 방법 중 택 1

#### environment.yml
" conda env create -f environment.yml " 아나콘다 가상환경 세팅 (모든 라이브러리 포함)

#### requirements.txt
" pip install -r requirements.txt "  직접 필요 라이브러리 설치


### 02. 통합모듈 조정