import numpy as np

def calculate_rank_stddev_by_years(filtered_table: str, base_table: str, years: list[int], conn) -> dict:
    cursor = conn.cursor()
    stddev_by_year = {}

    for yr in years:
        table_name = f"{base_table}_{yr}"
        query = f"""
            SELECT F.RK, E.RK_EST
            FROM {filtered_table} F
            JOIN {table_name} E
            ON F.ID = E.ID AND F.YR = E.YR
            WHERE F.RK IS NOT NULL AND E.RK_EST IS NOT NULL
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        diffs = [(int(rk) - int(est)) for rk, est in rows]

        if diffs:
            stddev = np.std(diffs)
            stddev_by_year[str(yr)] = stddev
        else:
            stddev_by_year[str(yr)] = None  # 또는 0, -1로 처리

    return stddev_by_year

def calculate_mean_stddev(stddev_by_year: dict) -> float:
    values = [v for v in stddev_by_year.values() if v is not None]
    return np.mean(values) if values else -1

def calculate_rank_error_by_years(filtered_table: str, base_table: str, years: list[int], conn) -> dict:
    cursor = conn.cursor()
    error_by_year = {}

    for yr in years:
        table_name = f"{base_table}_{yr}"
        query = f"""
            SELECT F.RK, E.RK_EST
            FROM {filtered_table} F
            JOIN {table_name} E
            ON F.ID = E.ID AND F.YR = E.YR
            WHERE F.RK IS NOT NULL AND E.RK_EST IS NOT NULL
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        year_error = sum((int(rk) - int(est)) ** 2 for rk, est in rows)
        error_by_year[str(yr)] = year_error

    return error_by_year
