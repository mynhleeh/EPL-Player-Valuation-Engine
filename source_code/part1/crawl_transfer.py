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
    
    try:
        # Chờ tối đa 8 giây để trang kịp hiển thị (Thay vì check is_element_present ngay lập tức làm hỏng logic)
        sb.wait_for_element("a.playerList-box", timeout=8)
    except Exception:
        return "N/a"

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
    
    # Khớp trên 80%
    if best_title and highest_score > 80:

        # Sử dụng CSS Selector để tránh lỗi cấu trúc với dấu nháy đơn trong tên (vd: O'Shea)
        safe_title = best_title.replace('"', '\\"')
        css_selector = f'a[title="{safe_title}"] span.player-tag'
        
        if sb.is_element_present(css_selector):
            return sb.get_text(css_selector).strip()
    
    return "N/a"

# Lưu dữ liệu từ DataFrame vào bảng price trong database
def store_database(price: pd.DataFrame, if_exists="replace"):
    with sqlite3.connect(str(DB_PATH)) as conn:
        price.to_sql("price", conn, if_exists=if_exists, index=False)


if __name__ == "__main__":
    all_names = get_names(DB_PATH)

    with SB(uc=True, headless=True) as sb:
        # Duyệt trực tiếp 1-1, bỏ qua thời gian nghỉ do web không check bot
        for index, n in enumerate(all_names):
            val = fetch_val(sb, n)
            print(f"{index}. {n}: {val}")
            
            # Ghi trực tiếp vào Database sau mỗi lượt thay vì chờ một đợt
            df_row = pd.DataFrame([{"Player": n, "Price": val}])
            
            # Cầu thủ đầu tiên tạo bảng/ghi đè, các cầu thủ sau nối thêm dữ liệu
            if index == 0:
                store_database(df_row, if_exists="replace")
            else:
                store_database(df_row, if_exists="append")
    