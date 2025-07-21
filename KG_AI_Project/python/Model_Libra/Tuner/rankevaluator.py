import numpy as np
from statistics import stdev

def calculate_rank_stddev_by_years(years: list, conn) -> dict:
    cursor = conn.cursor()
    stddevs = {}
    for y in years:
        col = f"SCR_EST_{y}"
        query = f"SELECT {col} FROM ESTIMATIONFLOW WHERE {col} IS NOT NULL"
        try:
            cursor.execute(query)
            scores = [row[0] for row in cursor.fetchall()]
            stddevs[str(y)] = round(stdev(scores), 4) if len(scores) > 1 else 0
        except Exception as e:
            print(f"[STDDEV 평가 오류] {y}년 → {e}")
            stddevs[str(y)] = -1
    return stddevs

def calculate_rank_error_by_years(years: list, conn) -> dict:
    cursor = conn.cursor()
    errors = {}
    for y in years:
        col = f"SCR_EST_{y}"
        query = f"SELECT {col} FROM ESTIMATIONFLOW WHERE {col} IS NOT NULL"
        try:
            cursor.execute(query)
            scores = [row[0] for row in cursor.fetchall()]
            if len(scores) > 0:
                mean = np.mean(scores)
                sq_errors = [(s - mean) ** 2 for s in scores]
                errors[str(y)] = int(sum(sq_errors))
            else:
                errors[str(y)] = 0
        except Exception as e:
            print(f"[ERROR 평가 오류] {y}년 → {e}")
            errors[str(y)] = -1
    return errors

def calculate_mean_stddev(stddevs: dict) -> float:
    values = [v for v in stddevs.values() if v >= 0]
    return round(sum(values) / len(values), 4) if values else -1