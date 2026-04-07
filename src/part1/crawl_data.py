import sqlite3
from seleniumbase import SB
from bs4 import BeautifulSoup

DB_NAME = "football_analysis_2024_2025.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS fbref_stats')
    # Thêm cột minutes_90s vào bảng
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fbref_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            squad TEXT,
            minutes INTEGER,
            minutes_90s REAL,
            goals TEXT,
            assists TEXT
        )
    ''')
    conn.commit()
    return conn

def crawl_fbref_90s():
    conn = init_db()
    cursor = conn.cursor()
    url = "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats"
    
    try:
        # Sử dụng SeleniumBase với UC để tránh Captcha
        with SB(uc=True, headless=False) as sb:
            print(f"[+] Đang mở trình duyệt lấy dữ liệu: {url}")
            sb.open(url)
            sb.wait_for_element("#stats_standard", timeout=20)
            
            # Lấy HTML động từ trình duyệt
            soup = BeautifulSoup(sb.get_page_source(), 'lxml')
            rows = soup.select("#stats_standard tbody tr:not(.thead)")
            
            players_saved = 0
            for row in rows:
                # Hàm lấy giá trị dựa trên data-stat
                def get_val(field):
                    cell = row.find(['td', 'th'], {"data-stat": field})
                    return cell.get_text(strip=True) if cell else "N/a"

                # Lấy số phút thực tế để lọc > 90 phút
                min_str = get_val("minutes").replace(",", "")
                minutes = int(min_str) if min_str.isdigit() else 0

                if minutes > 90:
                    name = get_val("player")
                    squad = get_val("team")
                    
                    # LẤY CHỈ SỐ 90s (data-stat="minutes_90s")
                    # Chỉ số này thường là số thập phân (VD: 1.5, 10.2)
                    nineties_val = get_val("minutes_90s")
                    try:
                        nineties = float(nineties_val)
                    except ValueError:
                        nineties = 0.0

                    goals = get_val("goals")
                    assists = get_val("assists")

                    # Lưu vào Database
                    cursor.execute('''
                        INSERT INTO fbref_stats (name, squad, minutes, minutes_90s, goals, assists)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (name, squad, minutes, nineties, goals, assists))
                    players_saved += 1
            
            conn.commit()
            print(f"[+] Hoàn tất! Đã lưu {players_saved} cầu thủ. Cột '90s' đã được thu thập.")

    except Exception as e:
        print(f"[-] Lỗi: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    crawl_fbref_90s()