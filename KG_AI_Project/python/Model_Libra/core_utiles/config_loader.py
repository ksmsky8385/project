import os
from dotenv import load_dotenv

load_dotenv()

ORACLE_USER         = os.getenv("ORACLE_USER")
ORACLE_PASSWORD     = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN          = os.getenv("ORACLE_DSN")
ORACLE_CLIENT_PATH  = os.getenv("ORACLE_CLIENT_PATH")

BASE_RAW_DIR        = os.getenv("BASE_RAW_DIR")
BASE_CSV_DIR        = os.getenv("BASE_CSV_DIR")
BASE_OUTPUT_DIR     = os.getenv("BASE_OUTPUT_DIR")

CSV_NUM06_PREFIX    = os.getenv("CSV_NUM06_PREFIX")
CSV_NUM07_PREFIX    = os.getenv("CSV_NUM07_PREFIX")
CSV_FILTERED_PREFIX = os.getenv("CSV_FILTERED_PREFIX")
