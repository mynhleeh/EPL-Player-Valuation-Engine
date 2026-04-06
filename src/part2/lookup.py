import requests
import argparse
import csv
from tabulate import tabulate

def main():
    # 1. Thiết lập công cụ để đọc chữ bạn gõ trên Terminal
    parser = argparse.ArgumentParser(description="Công cụ tra cứu cầu thủ bóng đá")
    parser.add_argument("--name", help="Tên cầu thủ cần tra cứu")
    parser.add_argument("--club", help="Tên câu lạc bộ cần tra cứu")
    
    # Lấy các giá trị người dùng vừa gõ
    args = parser.parse_args()

    # 2. Xây dựng đường link (gửi đến API mà bạn vừa làm ở bước trước)
    url = "http://127.0.0.1:5000/api/players"
    
    # Đóng gói các tham số name và club
    tham_so = {}
    if args.name:
        tham_so['name'] = args.name
    if args.club:
        tham_so['club'] = args.club

    # Kiểm tra xem người dùng có nhập gì không
    if not tham_so:
        print("Vui lòng nhập --name hoặc --club để tra cứu.")
        return

    print(f"Đang tìm kiếm với thông tin: {tham_so} ...")

    # 3. Gửi yêu cầu đến API (giống như lúc bạn F5 trên trình duyệt)
    try:
        response = requests.get(url, params=tham_so)
        
        # Nếu API trả về thành công (mã 200)
        if response.status_code == 200:
            data = response.json() # Chuyển dữ liệu về dạng danh sách Python
            
            # --- 1. IN RA MÀN HÌNH DƯỚI DẠNG BẢNG ---
            # Vì dữ liệu có rất nhiều cột, in hết sẽ bị vỡ bảng, 
            # nên ta chỉ trích xuất vài cột chính để xem cho đẹp.
            bang_hien_thi = []
            for row in data:
                bang_hien_thi.append([
                    row.get('Player'), row.get('Squad'), 
                    row.get('Nation'), row.get('Pos'), row.get('Age')
                ])
            headers_man_hinh = ["Tên cầu thủ", "Câu lạc bộ", "Quốc gia", "Vị trí", "Tuổi"]
            print(tabulate(bang_hien_thi, headers=headers_man_hinh, tablefmt="grid"))
            
            # --- 2. XUẤT RA FILE CSV ---
            # Tạo tên file dựa trên tham số đầu vào (thay thế dấu cách bằng dấu gạch dưới)
            ten_file = ""
            if args.name:
                ten_file = f"{args.name.replace(' ', '_')}.csv"
            else:
                ten_file = f"{args.club.replace(' ', '_')}.csv"
                
            # Lấy tên tất cả các cột từ dữ liệu của cầu thủ đầu tiên
            tat_ca_cot = data[0].keys()
            
            # Mở file và ghi dữ liệu
            with open(ten_file, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=tat_ca_cot)
                writer.writeheader() # Ghi dòng tiêu đề
                writer.writerows(data) # Ghi toàn bộ dữ liệu
                
            print(f"\n✅ Đã lưu toàn bộ chỉ số chi tiết vào file: {ten_file}")

        else:
            print("❌ Không tìm thấy cầu thủ hoặc câu lạc bộ này.")

    except requests.exceptions.ConnectionError:
        print("❌ Lỗi: Không thể kết nối đến API. Bạn đã bật app.py chưa?")

if __name__ == "__main__":
    main()