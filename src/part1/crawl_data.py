import sqlite3
import pandas as pd
import os
import io
import numpy as np
from seleniumbase import SB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def crawl_fbref_final():
    url = "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats"
    
    with SB(uc=True, headless=False) as sb:
        print("[1/4] Đang truy cập FBRef...")
        sb.open(url)
        try:
            sb.wait_for_element("#stats_standard", timeout=20)
            html_source = sb.get_page_source()
        except Exception as e:
            return print(f"Lỗi tải bảng: {e}")

    print("[2/4] Tối ưu hóa dữ liệu bằng thuật toán...")
    try:
        # 1. Đọc và lấy 25 cột đầu tiên
        df = pd.read_html(io.StringIO(html_source), attrs={'id': 'stats_standard'})[0]
        final_df = df[df.iloc[:, 1] != 'Player'].iloc[:, :25].copy()
        raw_cols = df.columns.get_level_values(1)[:25]

        # 2. Thuật toán đặt tên cột tự động (Ngắn gọn)
        counts = pd.Series(raw_cols).groupby(raw_cols).cumcount()
        totals = pd.Series(raw_cols).map(pd.Series(raw_cols).value_counts())
        
        new_cols = []
        for name, count, total in zip(raw_cols, counts, totals):
            if total > 1:
                suffix = "_performance" if count == 0 else "_per90minutes"
                new_cols.append(f"{name}{suffix}")
            else:
                new_cols.append(name)
        
        final_df.columns = new_cols

        # 3. Ép kiểu số & Làm sạch (Vectorized)
        final_df['Age'] = final_df['Age'].str[:2]
        final_df['Nation'] = final_df['Nation'].str.split().str[-1].fillna("N/a")

        # Chuyển tất cả cột có thể sang số, lọc > 90 phút
        cols_to_fix = final_df.columns.difference(['Player', 'Nation', 'Pos', 'Squad', 'Matches'])
        final_df[cols_to_fix] = final_df[cols_to_fix].apply(pd.to_numeric, errors='coerce')
        final_df = final_df[final_df['Min'] > 90].reset_index(drop=True)

        # 4. Chuyển 0 thành NULL (NaN) trừ cột Rk
        null_targets = cols_to_fix.difference(['Rk'])
        final_df[null_targets] = final_df[null_targets].replace({0: np.nan, 0.0: np.nan})

        print(f"[3/4] Ghi {len(final_df)} dòng vào database...")
        with sqlite3.connect(DB_PATH) as conn:
            final_df.to_sql("statistic", conn, if_exists="replace", index=False)
        
        print("HOÀN TẤT!")

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    crawl_fbref_final()