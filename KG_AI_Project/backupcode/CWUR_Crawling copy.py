import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

def extract_years_from_filenames(folder):
    years = []
    for fname in os.listdir(folder):
        match = re.search(r'_(\d{4})\.csv$', fname)
        if match:
            years.append(int(match.group(1)))
    return sorted(set(years))

def crawl_cwur_for_year(year):
    url = f"https://cwur.org/{year}.php"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
        res = requests.get(url, headers=headers)
        print(f"🔗 요청 URL: {url}")
        print(f"📡 응답 코드: {res.status_code}")
        print(f"🧾 응답 길이: {len(res.text)}")
        print(f"📄 일부 HTML:\n{res.text[:500]}")
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

    
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("table tr")
    data = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 8 and "South Korea" in cols[2].text:
            institution = cols[1].text.strip()
            score = cols[7].text.strip()
            data.append({"Institution": institution, "Score": score, "Year": year})

    return data

def save_scores_to_csv(all_data, output_dir):
    df = pd.DataFrame(all_data)
    df.to_csv(os.path.join(output_dir, "cwur_korea_scores.csv"), index=False, encoding="utf-8-sig")
    
    

if __name__ == "__main__":
    folder_path = r"D:\workspace\project\KG_AI_Project\resource\csv_files\csv_data"
    output_dir = r"D:\workspace\project\KG_AI_Project\resource\csv_files"

    # 1️⃣ 연도 추출
    years = extract_years_from_filenames(folder_path)
    print(f"📅 추출된 연도들: {years}")

    # 2️⃣ 크롤링 실행
    all_data = []
    for year in years:
        print(f"🛠️ 크롤링 중: {year}")
        result = crawl_cwur_for_year(year)
        all_data.extend(result)

    # 3️⃣ 저장
    save_scores_to_csv(all_data, output_dir)
    print("✅ CWUR 데이터 저장 완료")