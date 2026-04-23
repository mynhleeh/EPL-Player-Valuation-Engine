import sqlite3
import pandas as pd
import time
import urllib.parse
from pathlib import Path
from seleniumbase import SB
from thefuzz import fuzz

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "database.db"


def get_names(path):

    # Lấy danh sách cầu thủ trong statistic
    with sqlite3.connect(str(path)) as conn:
        df = pd.read_sql("SELECT Player FROM statistic", conn)
        print("Loaded players from database")
        return df['Player'].tolist()


def fetch_val(sb, name):

    # Tìm cầu thủ trên FootballTransfers, lấy giá trị chuyển nhượng
    url = f"https://www.footballtransfers.com/en/search?search_value={urllib.parse.quote(name)}"
    sb.open(url)
    
    if not sb.is_element_present("a.playerList-box"):
        return "N/a"

    sb.wait_for_element("a.playerList-box", timeout=20)
    boxes = sb.find_elements("a.playerList-box")

    best_title = None
    highest_score = 0

    # Tìm title có độ khớp cao nhất
    for b in boxes:
        title = b.get_attribute("title")
        if not title:
            continue
        
        score = fuzz.token_sort_ratio(name.lower(), title.strip().lower())
        if score > highest_score:
            highest_score = score
            best_title = title.strip()
    
    # Khớp trên 80%, dùng XPath để lấy giá trị chuyển nhượng 
    if best_title and highest_score > 80:

        # XPath này tìm thẻ 'a' có title tương ứng, sau đó lấy thẻ span con của nó
        xpath = f"//a[@title='{best_title}']//span[@class='player-tag']"
        if sb.is_element_present(xpath):
            return sb.get_text(xpath).strip()
    
    return "N/a"

# Lưu dữ liệu từ DataFrame vào bảng price trong database
def store_database(price: pd.DataFrame):
    with sqlite3.connect(str(DB_PATH)) as conn:
        price.to_sql("price", conn, if_exists="replace", index=False)


if __name__ == "__main__":
    all_names = get_names(DB_PATH)
    results = []
    
    # Cấu hình chia đợt
    CHUNK_SIZE = 50

    with SB(uc=True, headless=True) as sb:
        # Duyệt danh sách theo từng đợt 50 cầu thủ
        for i in range(0, len(all_names), CHUNK_SIZE):
            chunk = all_names[i : i + CHUNK_SIZE]
            
            for index, n in enumerate(chunk):
                val = fetch_val(sb, n)
                # i + index để hiển thị đúng số thứ tự tổng quát trong log
                print(f"{i + index}. {n}: {val}")
                results.append({"Player": n, "Price": val})
                
                # Nghỉ ngắn giữa mỗi cầu thủ để mô phỏng người dùng thật
                time.sleep(1)

            # Sau khi duyệt xong một đợt (50 người), nghỉ 15 giây trước khi tiếp tục
            if i + CHUNK_SIZE < len(all_names):
                time.sleep(15)
    
    df_results = pd.DataFrame(results)
    store_database(df_results)
    