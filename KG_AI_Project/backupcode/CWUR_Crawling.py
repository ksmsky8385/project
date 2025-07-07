import os
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_years_from_filenames(folder):
    years = []
    for fname in os.listdir(folder):
        match = re.search(r'_(\d{4})\.csv$', fname)
        if match:
            years.append(int(match.group(1)))
    return sorted(set(years))

def get_cwur_url(year):
    if 2018 <= year <= 2022:
        return f"https://cwur.org/{year}-{str(year+1)[-2:]}.php"
    else:
        return f"https://cwur.org/{year}.php"

# 🎯 컬럼명 후보 리스트 기반 인덱스 찾기 함수
def find_column_index(candidates, headers):
    for col in candidates:
        if col in headers:
            return headers.index(col)
    return None

def crawl_cwur_by_selenium(year):
    url = get_cwur_url(year)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # 테이블 로딩 대기
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
    except:
        print(f"❌ 연도 {year}: 테이블 로딩 실패")
        driver.quit()
        return []

    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")
    if not table:
        print(f"❌ 연도 {year}: 테이블 없음")
        return []

    header_row = table.find("tr")
    if not header_row:
        print(f"❌ 연도 {year}: 테이블 헤더 없음")
        return []

    headers = [th.text.strip() for th in header_row.find_all("th")]

    # 🧠 컬럼명 후보 리스트
    location_candidates = ["Location", "Country"]
    institution_candidates = ["Institution"]
    score_candidates = ["Score", "Overall Score"]

    loc_idx = find_column_index(location_candidates, headers)
    inst_idx = find_column_index(institution_candidates, headers)
    score_idx = find_column_index(score_candidates, headers)

    # 누락된 컬럼 안내
    missing = []
    if loc_idx is None: missing.append("Location/Country")
    if inst_idx is None: missing.append("Institution")
    if score_idx is None: missing.append("Score")
    if missing:
        print(f"❌ 연도 {year}: 누락된 컬럼 - {', '.join(missing)}")
        return []

    # 데이터 추출
    data = []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) > max(loc_idx, inst_idx, score_idx):
            location = cols[loc_idx].text.strip()
            if location == "South Korea":
                institution = cols[inst_idx].text.strip()
                score = cols[score_idx].text.strip()
                data.append({
                    "Institution": institution,
                    "Score": score,
                    "Year": year
                })

    return data

def save_scores_to_csv(all_data, output_path):
    df = pd.DataFrame(all_data)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 저장 완료: {output_path}")

if __name__ == "__main__":
    folder_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"
    output_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\cwur_korea_scores_selenium.csv"

    years = extract_years_from_filenames(folder_path)
    print(f"📅 추출된 연도들: {years}")

    all_data = []
    for year in years:
        print(f"🚀 크롤링 중: {year}")
        result = crawl_cwur_by_selenium(year)
        all_data.extend(result)

    save_scores_to_csv(all_data, output_path)