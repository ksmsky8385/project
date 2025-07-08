def validate_columns(df, required):
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"다음 컬럼이 누락되었습니다: {missing}")