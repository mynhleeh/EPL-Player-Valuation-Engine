import sqlite3
import pandas as pd
import time
import urllib.parse
from pathlib import Path
from seleniumbase import SB

# 1. Gộp đường dẫn thành 1 dòng duy nhất bằng pathlib
# Lùi 2 cấp từ file script (part1 -> source_code -> PY_PROJECT) để vào data/database.db
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "database.db"

def get_names(path):
    if not path.exists():
        print(f"Error: Database not found at {path}")
        return []
    
    conn = sqlite3.connect(str(path))
    try:
        # BỎ DISTINCT để lấy đủ tất cả các dòng (502 dòng) trong bảng statistic
        df = pd.read_sql("SELECT Player FROM statistic", conn)
        print(f"Successfully loaded {len(df)} players from database.")
        return df['Player'].tolist()
    finally:
        conn.close()

def fetch_val(sb, name):
    url = f"https://www.footballtransfers.com/en/search?search_value={urllib.parse.quote(name)}"
    try:
        sb.open(url)
        # Tối ưu: Đợi phần tử hiện ra thay vì sleep cố định
        sb.wait_for_element("a.playerList-box", timeout=7)
        
        boxes = sb.find_elements("a.playerList-box")
        for b in boxes:
            try:
                title = b.get_attribute("title").strip()
                # Kiểm tra độ khớp của tên để tránh lấy nhầm người
                if name.lower() in title.lower() or title.lower() in name.lower():
                    if len(name.split()) == 1 and name.lower() != title.lower():
                        continue
                    return sb.get_text("span.player-tag").strip()
            except:
                continue
        return "N/a"
    except:
        return "N/a"

def update_price_to_db(results, path):
    """Cập nhật trực tiếp giá trị vào cột Price của bảng players"""
    try:
        with sqlite3.connect(str(path)) as conn:
            cursor = conn.cursor()
            # Sử dụng executemany để cập nhật hàng loạt, tối ưu tốc độ ghi đĩa
            cursor.executemany("""
                UPDATE players 
                SET Price = ? 
                WHERE Player = ?
            """, [(r['Transfer_Value'], r['Player']) for r in results])
            conn.commit()
        print(f"--- Updated {len(results)} records in 'players' table ---")
    except Exception as e:
        print(f"Error updating database: {e}")

def main():
    print(f"Targeting Database at: {DB_PATH}")
    all_names = get_names(DB_PATH)
    if not all_names: return 
    
    results = []
    
    # Chạy ngầm (headless=True) để MacBook không bị nóng và tốn RAM
    with SB(uc=True, headless=True) as sb:
        for i, n in enumerate(all_names):
            val = fetch_val(sb, n)
            results.append({"Player": n, "Transfer_Value": val})
            
            # In tiến độ thực tế (ví dụ: [100/502])
            print(f"[{i+1}/{len(all_names)}] {n}: {val}")
            
            # Cứ mỗi 50 người thì lưu vào DB một lần để tránh mất dữ liệu nếu gặp sự cố
            if (i + 1) % 50 == 0:
                update_price_to_db(results, DB_PATH)
                results = [] # Reset danh sách tạm
                time.sleep(3) # Nghỉ ngắn để tránh bị website chặn IP
            
            time.sleep(0.3) # Nghỉ nhẹ giữa mỗi lần crawl

    # Lưu nốt những cầu thủ còn lại sau vòng lặp
    if results:
        update_price_to_db(results, DB_PATH)

if __name__ == "__main__":
    main()