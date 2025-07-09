# Model_Libra 프로젝트 패키지 구성

### 00. 디렉토리 구성 및 설명

Model_Libra/  
│  
├── core_utiles/ <- 공통 모듈 전용 폴더  
│   ├── __init__.py  
│   ├── config_loader.py <- .env 로드 모듈   
│   ├── Mapper.py <- 헤더, 대학명 매핑표 모듈  
│   ├── OracleDBConnection.py <- 오라클DB 접속 모듈  
│   ├── OracleSchemaBuilder.py <- 테이블 생성 시 데이터타입 보정 모듈  
│   └── OracleTableCreater.py <- 데이터타입 보정 후 테이블 생성 모듈  
│   ├── Tool_HeaderConvorter.py <- 전처리 데이터 컬럼 한영 변환툴  
│   ├── Tool_HeaderRemaker.py <- 전처리 데이터 컬럼 가독성 보완툴  
│  
├── DataHandling/ <- 원본파일 CSV파일화 및 DB 업로드 패키지  
│   ├── __init__.py  
│   ├── __main__.py <- DataHandling 패키지 실행  
│   ├── CSVHeaderRenamer.py <- 모든 csv파일 컬럼 별 헤더 영문약어로 변경 클래스  
│   ├── CSVToOracleUploader.py <- 오라클DB로 모든 csv파일 테이블 생성 클래스  
│   ├── CWURCrawler.py <- CWUR 사이트 대학 평가점수 크롤링 클래스  
│   ├── EnNameCollector.py <- 크롤링 데이터 영문 대학명 리스트화 클래스  
│   ├── ExcelToCSVConverter_ver1.py <- CSV파일 변환 클래스 1  
│   ├── ExcelToCSVConverter_ver2.py <- CSV파일 변환 클래스 2  
│   ├── HeaderAbbreviationMapper.py <- 헤더 한글 영문 매핑 클래스  
│   ├── HeaderTermCollector.py <- 모든 csv파일 컬럼 별 헤더 수집 클래스  
│   ├── NameMapper.py <- 영문 대학명 한국명으로 매핑 클래스  
│   └── RankedScoreExporter.py <- 연도 별 대학 평가점수 csv 파일 생성  
│  
├── DBHandling/ <- 생성된 DB테이블 기반 전처리 및 정규화 패키지  
│   ├── __init__.py  
│   ├── __main__.py <- DBHandling 패키지 실행  
│   ├── DataMergerAndExporter.py <- 평가점수 + 대학 별 데이터 병합 및 테이블 생성 클래스  
│   ├── FilteredScoreUploader.py <- 인풋 & 타깃 컬럼 정규화 테이블 생성 클래스  
│   └── TableMergerUploader.py <- 모든 데이터테이블 연도별로 병합 및 테이블 생성 클래스  
│  
├── EstimationFlow/ <- RFR 모델을 이용한 예측데이터 테이블링 패키지  
│   ├── __init__.py  
│   ├── __main__.py <- EstimationFlow 패키지 실행  
│   ├── ModelLoader.py <- 머신러닝 모델 로딩 클래스  
│   ├── SCRTableBuilder.py <- 모든 대학 별 점수 예측 및 예측점수 포함 테이블 생성 클래스  
│   └── SCRTableUpdater.py <- 생성된 테이블에 등수 및 피쳐값 병합 업데이트 클래스  
│  
├── EstimationFuture/ <- XGB 모델을 이용한 예측데이터 테이블링 패키지  
│   ├── __init__.py  
│   ├── __main__.py <- EstimationFlow 패키지 실행  
│   ├── ModelLoader.py <- 머신러닝 모델 로딩 클래스  
│   ├── SCRTableBuilder.py <- 예측된 미래점수 테이블 생성 클래스  
│   └── SCRTableUpdater.py <- 미래점수값을 이용한 추이 데이터 추가 업데이트 클래스  
│  
├── ML_RFR/ <- 렌덤포레스트 회귀 머신러닝 모델 패키지  
│   ├── models/  
│   │   └── model_rfr_v1.0.pkl <- 초기모델 피클파일  
│   ├── utils/   
│   │   ├── __init__.py  
│   │   ├── evaluator.py <- 회귀 예측 결과 평가 지표 계산 모듈 (RMSE)  
│   │   └── validator.py <- 입력/출력 데이터 유효성 검증 모듈  
│   ├── __init__.py  
│   ├── __main__.py <- ML_RFR 패키지 실행  
│   ├── cleaner.py <- 학습 데이터 전처리 및 결측치 처리 클래스  
│   ├── config.py <- 모델 설정값, 하이퍼파라미터 등 환경설정 로딩 클래스  
│   ├── controller.py <- 전체 파이프라인 흐름 제어 클래스  
│   ├── exporter.py <- 학습된 모델 피클 익스포트 클래스  
│   ├── fetcher.py <- DB에서 학습 데이터 추출 클래스  
│   ├── model.py <- RandomForest 모델 생성 및 설정 클래스  
│   ├── predictor.py <- 학습된 모델 불러와서 예측 수행 클래스  
│   └── trainer.py <- 모델 학습 로직 및 하이퍼파라미터 설정 클래스  
│  
├── ML_XGB/ <- XGBoost 회귀 머신러닝 모델 패키지  
│   ├── models/  
│   │   └── model_xgb_v1.0.pkl <- 초기모델 피클파일  
│   ├── utils/   
│   │   ├── __init__.py  
│   │   ├── evaluator.py <- 회귀 예측 결과 평가 지표 계산 모듈 (RMSE)  
│   │   └── validator.py <- 입력/출력 데이터 유효성 검증 모듈  
│   ├── __init__.py  
│   ├── __main__.py <- ML_XGB 패키지 실행  
│   ├── cleaner.py <- 학습 데이터 전처리 및 결측치 처리 클래스  
│   ├── config.py <- 모델 설정값, 하이퍼파라미터 등 환경설정 로딩 클래스  
│   ├── controller.py <- 전체 파이프라인 흐름 제어 클래스  
│   ├── exporter.py <- 학습된 모델 피클 익스포트 클래스  
│   ├── fetcher.py <- DB에서 학습 데이터 추출 클래스  
│   ├── model.py <- XGBoost 모델 생성 및 설정 클래스  
│   ├── predictor.py <- 학습된 모델 불러와서 예측 수행 클래스  
│   └── trainer.py <- 모델 학습 로직 및 하이퍼파라미터 설정 클래스  
│  
├── __init__.py  
├── __main__.py <- Model_Libra 내부 패키지 전체 실행  
├── .env.template <- 계정 및 패스 설정  
├── environment.yml <- " conda env create -f environment.yml " 아나콘다 가상환경 세팅  
├── README.md <- 설명글  
└── requirements.txt <- " pip install -r requirements.txt " 필요 라이브러리 설치  





### 01. 환경세팅

두가지 방법 중 택 1

1. environment.yml
" conda env create -f environment.yml " 아나콘다 가상환경 세팅 (모든 라이브러리 포함)

2. requirements.txt
" pip install -r requirements.txt "  직접 필요 라이브러리 설치


### 02. 통합모듈 조정