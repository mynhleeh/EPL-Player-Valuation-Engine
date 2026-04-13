import sqlite3
import pandas as pd
import time
import urllib.parse
import os
from seleniumbase import SB

# Lấy đường dẫn thư mục hiện tại của file script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Kết hợp với cấu trúc thư mục con để tìm file database.db
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")

# 1. Lấy dữ liệu từ DB
def get_names(path):
    # Kiểm tra xem file có tồn tại không trước khi kết nối
    if not os.path.exists(path):
        print(f"Error: Database not found at {path}")
        return []
    
    conn = sqlite3.connect(path)
    try:
        df = pd.read_sql("SELECT DISTINCT Player FROM statistic", conn)
        print("Names loaded")
        return df['Player'].tolist()
    finally:
        conn.close()

# 2. Thu thập giá trị từ Web
def fetch_val(sb, name):
    url = f"https://www.footballtransfers.com/en/search?search_value={urllib.parse.quote(name)}"
    try:
        sb.open(url)
        sb.sleep(6)
        boxes = sb.find_elements("a.playerList-box")
        for b in boxes:
            try:
                title = b.get_attribute("title").strip()
                if name.lower() in title.lower() or title.lower() in name.lower():
                    if len(name.split()) == 1 and name.lower() != title.lower():
                        continue
                    return sb.get_text("span.player-tag").strip()
            except:
                continue
        return "N/a"
    except:
        return "N/a"

# 3. Làm sạch dữ liệu
def clean_df(data):
    df = pd.DataFrame(data)
    df['Transfer_Value'] = df['Transfer_Value'].fillna("N/a")
    print("Data cleaned")
    return df

# 4. Lưu vào SQL
def save_db(df, path):
    with sqlite3.connect(path) as conn:
        df.to_sql("transfer_values", conn, if_exists="replace", index=False)
    print("Exported to SQL")

# 5. Điều phối chính
def main_test():
    names = get_names(DB_PATH)
    if not names: return # Dừng nếu không tìm thấy database hoặc không có tên
    
    results = []
    with SB(uc=True, headless=False) as sb:
        for n in names:
            val = fetch_val(sb, n)
            print(f"{n}: {val}") 
            results.append({"Player": n, "Transfer_Value": val})
            time.sleep(1.5)
    print("Collected Data")

    final_df = clean_df(results)
    save_db(final_df, DB_PATH)

if __name__ == "__main__":
    main_test()