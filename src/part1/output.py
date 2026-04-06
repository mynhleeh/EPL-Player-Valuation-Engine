import sqlite3
from prettytable import PrettyTable

def display_captured_data():
    db_name = "football_analysis_2024_2025.db"
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 1. Kiểm tra sự tồn tại của bảng (Tránh lỗi nếu chưa crawl xong)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fbref_stats'")
        if not cursor.fetchone():
            print("[-] LỖI: Bảng 'fbref_stats' chưa tồn tại. Hãy chạy file crawl động trước!")
            return

        # 2. Truy vấn kết hợp (JOIN) 2 bảng dữ liệu
        # Sử dụng COLLATE NOCASE để so khớp tên không phân biệt hoa thường
        query = '''
            SELECT 
                f.name, 
                f.squad, 
                f.minutes,
                f.goals, 
                f.assists, 
                f.xG,
                t.transfer_value
            FROM fbref_stats f
            LEFT JOIN transfer_values t ON f.name = t.player_name COLLATE NOCASE
            WHERE f.minutes > 90
            ORDER BY 
                CAST(f.goals AS INTEGER) DESC, 
                f.minutes DESC
            LIMIT 50
        '''
        
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("(!) Không tìm thấy dữ liệu phù hợp. Có thể do chưa crawl đủ 90 phút thi đấu.")
            return

        # 3. Khởi tạo PrettyTable
        table = PrettyTable()
        table.field_names = ["STT", "Tên Cầu Thủ", "CLB", "Số Phút", "Bàn Thắng", "Kiến Tạo", "xG", "Giá Trị (ETV)"]
        
        # Căn lề cho đẹp
        table.align["Tên Cầu Thủ"] = "l"
        table.align["CLB"] = "l"
        table.align["Giá Trị (ETV)"] = "r"
        table.align["Số Phút"] = "r"

        # 4. Xử lý dữ liệu dòng và trang trí
        for index, row in enumerate(rows, start=1):
            name, squad, mins, gls, ast, xg, price = row
            
            # Xử lý hiển thị giá trị: Nếu null hoặc N/a thì báo "Chưa cập nhật"
            display_price = price if price and price != "N/a" else "---"
            
            # Highlight các siêu sao ghi trên 5 bàn (điều chỉnh theo mùa giải hiện tại)
            display_name = name
            try:
                if gls != "N/a" and int(gls) >= 5:
                    display_name = f"⭐ {name}"
            except:
                pass
                
            table.add_row([index, display_name, squad, mins, gls, ast, xg, display_price])

        # 5. Giao diện xuất báo cáo
        header = "BÁO CÁO PHÂN TÍCH DỮ LIỆU CẦU THỦ (DYNAMIC CRAWL 2024-2025)"
        print("\n" + "═"*115)
        print(f"{header:^115}")
        print("═"*115)
        print(table)
        
        # 6. Thống kê nhanh hiệu quả khớp dữ liệu (Data Integrity)
        cursor.execute("SELECT COUNT(*) FROM fbref_stats")
        total_p = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transfer_values WHERE transfer_value != 'N/a' AND transfer_value IS NOT NULL")
        found_p = cursor.fetchone()[0]
        
        rate = (found_p / total_p * 100) if total_p > 0 else 0

        print(f"\n[i] Tổng số cầu thủ trong DB: {total_p}")
        print(f"[i] Cầu thủ đã tìm thấy giá (ETV): {found_p} ({rate:.1f}%)")
        print("[*] Ghi chú: Dữ liệu được cập nhật từ hệ thống cào động Selenium UC Mode.\n")

    except Exception as e:
        print(f"[-] Lỗi hiển thị: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    display_captured_data()