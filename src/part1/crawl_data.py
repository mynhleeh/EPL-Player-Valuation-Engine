import sqlite3
import pandas as pd
import os
import io
import numpy as np
from seleniumbase import SB

# Thiết lập đường dẫn và tạo thư mục data nếu chưa có
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_PATH = os.path.join(DATA_DIR, "database.db")

def get_html(url):
    """Lấy HTML từ web"""
    with SB(uc=True, headless=False) as sb:
        sb.open(url)
        try:
            sb.wait_for_element("#stats_standard", timeout=20)
            html = sb.get_page_source()
            print("Collected Data")
            return html
        except:
            return None

def rename_cols(html):
    """Đổi tên cột theo vị trí index"""
    df = pd.read_html(io.StringIO(html), attrs={'id': 'stats_standard'})[0]
    df = df[df.iloc[:, 1] != 'Player'].iloc[:, :25].copy()
    raw = df.columns.get_level_values(1)[:25]

    cols = []
    for i, name in enumerate(raw):
        if 11 <= i <= 18:
            cols.append(f"{name}_perf")
        elif 19 <= i <= 23:
            cols.append(f"{name}_per90")
        else:
            cols.append(name)
    
    df.columns = cols
    print("Renamed Columns")
    return df

def clean_data(df):
    """Làm sạch và xử lý dữ liệu"""
    if 'Age' in df.columns:
        df['Age'] = df['Age'].str[:2]
    if 'Nation' in df.columns:
        df['Nation'] = df['Nation'].str.split().str[-1].fillna("N/a")

    exc = ['Player', 'Nation', 'Pos', 'Squad', 'Matches']
    fix = [c for c in df.columns if c not in exc]
    
    df[fix] = df[fix].apply(pd.to_numeric, errors='coerce')
    
    if 'Min' in df.columns:
        df = df[df['Min'] > 90].reset_index(drop=True)

    nulls = [c for c in fix if c != 'Rk']
    df[nulls] = df[nulls].replace({0: np.nan, 0.0: np.nan})
    
    print("Cleaned Data")
    return df

def save_db(df, path):
    """Lưu vào SQL trong thư mục data"""
    with sqlite3.connect(path) as conn:
        df.to_sql("statistic", conn, if_exists="replace", index=False)
    print("Saved to SQL")

def main():
    url = "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats"
    
    html = get_html(url)
    if not html: return

    df = rename_cols(html)
    df = clean_data(df)
    save_db(df, DB_PATH)

if __name__ == "__main__":
    main()