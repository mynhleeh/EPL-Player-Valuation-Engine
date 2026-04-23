import sqlite3
import pandas as pd
import os
import io
import numpy as np
from seleniumbase import SB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Lùi 2 cấp từ source_code/part1/ để vào data/
DB_PATH = os.path.join(BASE_DIR, "..", "..", "data", "database.db")

def get_html(url):
    # Sử dụng SeleniumBase (UC mode) để vượt rào và lấy mã nguồn HTML từ website
    with SB(uc=True, headless=True) as sb:
        sb.open(url)
        try:
            sb.wait_for_element("#stats_standard", timeout=20)
            html = sb.get_page_source()
            print("Successfully fetched HTML data from the website.")
            return html
        except Exception:
            print("Failed to fetch data: Element not found or timeout.")
            return None

def rename_cols(html):
    # Chuyển HTML thành DataFrame, xử lý cột đa tầng và định dạng lại tên cột
    df = pd.read_html(io.StringIO(html), attrs={'id': 'stats_standard'})[0]
    df = df[df.iloc[:, 1] != 'Player'].copy()

    new_cols = []
    for col in df.columns:
        lvl0 = str(col[0])
        lvl1 = str(col[1])
        
        if "Performance" in lvl0:
            new_cols.append(f"{lvl1}_perf")
        elif "Per 90" in lvl0:
            new_cols.append(f"{lvl1}_per90")
        else:
            new_cols.append(lvl1)  
            
    df.columns = new_cols
    return df.iloc[:, :25]

def clean_data(df):
    # Ép kiểu dữ liệu số cho các chỉ số và lọc cầu thủ thi đấu trên 90 phút
    exc = ['Player', 'Nation', 'Pos', 'Squad', 'Matches']
    fix = [c for c in df.columns if c not in exc]
    
    # Ép kiểu dữ liệu số cho các cột chỉ số
    df[fix] = df[fix].apply(pd.to_numeric, errors='coerce')

    # Lọc cầu thủ đá trên 90 phút để dữ liệu có ý nghĩa hơn
    if 'Min' in df.columns:
        df = df[df['Min'] > 90].reset_index(drop=True)

    return df

def save_to_statistic_table(df, path):
    # Kết nối và lưu dữ liệu vào bảng 'statistic' trong SQLite (ghi đè nếu tồn tại)
    with sqlite3.connect(path) as conn:
        df.to_sql("statistic", conn, if_exists="replace", index=False)
        print("Successfully saved data to the database.")
   
if __name__ == "__main__":
    url = "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats"
    html = get_html(url)
    if html:
        df = rename_cols(html)
        df = clean_data(df)
        save_to_statistic_table(df, DB_PATH)
    else:
        print("Crawl failed: No HTML content to process.")