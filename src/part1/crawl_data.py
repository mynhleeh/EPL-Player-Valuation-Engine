import sqlite3
import time
import random
import re
import urllib.parse
from seleniumbase import SB
from bs4 import BeautifulSoup

DB_NAME = "football_analysis_2024_2025.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS fbref_stats')
    cursor.execute('DROP TABLE IF EXISTS transfer_values')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fbref_stats (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, nation TEXT, pos TEXT, squad TEXT, age TEXT, 
            born TEXT, minutes INTEGER, goals TEXT, assists TEXT, xG TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transfer_values (
            player_name TEXT PRIMARY KEY,
            transfer_value TEXT
        )
    ''')
    conn.commit()
    return conn

def crawl_football_data():
    conn = init_db()
    cursor = conn.cursor()

    try:
        with SB(uc=True, headless=False) as sb:
            # --- BƯỚC 1: FBRef ---
            url_fbref = "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats"
            sb.open(url_fbref)
            sb.wait_for_element("#stats_standard", timeout=20) # Đợi bảng xuất hiện

            soup = BeautifulSoup(sb.get_page_source(), 'lxml')
            rows = soup.select("#stats_standard tbody tr:not(.thead)")
            
            players_to_search = []
            
            for row in rows:
                try:
                    # SỬA Ở ĐÂY: Lấy tên an toàn hơn
                    name_cell = row.find(['td', 'th'], {"data-stat": "player"})
                    if not name_cell: continue
                    name = name_cell.get_text(strip=True)

                    min_el = row.select_one("td[data-stat='minutes']")
                    minutes = int(min_el.text.replace(",", "")) if min_el and min_el.text.strip().replace(",", "").isdigit() else 0

                    if minutes > 90:
                        def get_val(stat_name):
                            el = row.select_one(f"td[data-stat='{stat_name}']")
                            return el.text.strip() if el and el.text.strip() else "N/a"

                        goals = get_val('goals')
                        assists = get_val('assists')
                        xg = get_val('xg')
                        
                        age = get_val('age')
                        if age != "N/a": age = age[:2]
                        
                        born = get_val('birth_year')
                        nation = get_val('nationality')
                        # Xoá mã qgia thừa (vd 'eng ENG' -> 'ENG')
                        if nation != "N/a" and " " in nation: nation = nation.split()[-1]
                        
                        pos = get_val('position')
                        squad = get_val('team')

                        cursor.execute('''
INSERT INTO fbref_stats (name, nation, pos, squad, age, born, minutes, goals, assists, xG)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (name, nation, pos, squad, age, born, minutes, goals, assists, xg))
                        players_to_search.append(name)
                except Exception as e:
                    continue
            
            conn.commit() # Lưu toàn bộ cầu thủ vào DB ngay
            print(f"[+] Đã lưu {len(players_to_search)} cầu thủ vào FBRef_stats")

            # --- BƯỚC 2: Transfer Values ---
            print("[+] Bắt đầu thu thập giá chuyển nhượng (Sẽ tốn thời gian do có sleep chống rate-limit)...")
            
            # Lấy dữ liệu tên cầu thủ sau khi crawl từ database
            cursor.execute("SELECT name FROM fbref_stats")
            players_db = [row[0] for row in cursor.fetchall()]

            for player in players_db:
                try:
                    # Làm sạch tên cầu thủ theo hướng dẫn
                    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', player)
                    query = urllib.parse.quote(clean_name)
                    
                    search_url = f"https://www.footballtransfers.com/en/search?search_value={query}"
                    sb.open(search_url)
                    
                    # Đợi giá trị xuất hiện hoặc trang tìm kiếm xuất hiện (Thêm random chống bot)
                    sb.sleep(random.uniform(2, 4))
                    
                    if sb.is_element_visible("a.player-tag", timeout=3):
                        sb.click("a.player-tag")
                        sb.sleep(random.uniform(1.5, 3))

                    value = "N/a"
                    if sb.is_element_present("span.etv-value", timeout=3):
                        value = sb.get_text("span.etv-value").strip()
                    
                    cursor.execute('INSERT OR REPLACE INTO transfer_values (player_name, transfer_value) VALUES (?, ?)', (player, value))
                    print(f"   -> {player}: {value}")
                except Exception as e:
                    cursor.execute('INSERT OR REPLACE INTO transfer_values (player_name, transfer_value) VALUES (?, ?)', (player, "N/a"))
            
            conn.commit() # Commit lần cuối cho bảng giá trị

    except Exception as e:
        print(f"[-] Lỗi nghiêm trọng: {e}")
    finally:
        conn.close()
        print("[!] Đã đóng kết nối Database.")

if __name__ == "__main__":
    crawl_football_data()