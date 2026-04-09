import requests
import argparse
import csv
from tabulate import tabulate
from pathlib import Path

# --- HÀM 1: CHUYÊN GỌI API ---
def fetch_player_data(name, club):
    url = "http://127.0.0.1:5000/api/players"
    tham_so = {}
    if name: tham_so['name'] = name
    if club: tham_so['club'] = club

    try:
        response = requests.get(url, params=tham_so)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print("❌ Không tìm thấy cầu thủ hoặc câu lạc bộ này.")
            return None
        else:
            print(f"❌ Lỗi từ Server (Mã: {response.status_code})")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Lỗi: Không thể kết nối đến API. Bạn đã bật app.py chưa?")
        return None

# --- HÀM 2: CHUYÊN VẼ BẢNG ---
def display_table(data):
    bang_hien_thi = []
    for row in data:
        bang_hien_thi.append([
            row.get('Player'), row.get('Squad'), 
            row.get('Nation'), row.get('Pos'), row.get('Age')
        ])
    headers = ["Tên cầu thủ", "Câu lạc bộ", "Quốc gia", "Vị trí", "Tuổi"]
    print(tabulate(bang_hien_thi, headers=headers, tablefmt="grid"))

# --- HÀM 3: CHUYÊN LƯU FILE CSV ---
def save_to_csv(data, args):
    current_dir = Path(__file__).parent
    thu_muc_luu = current_dir.parent.parent / 'data' / 'lookup_ans'
    thu_muc_luu.mkdir(parents=True, exist_ok=True) 

    # Tối ưu việc đặt tên: Nếu nhập cả 2, tên file sẽ có cả tên và clb
    if args.name and args.club:
        ten_file = f"{args.name}_{args.club}.csv"
    elif args.name:
        ten_file = f"{args.name}.csv"
    else:
        ten_file = f"{args.club}.csv"
        
    # Tên file hợp lệ trên Windows
    ten_file = ten_file.replace(' ', '_') 
    duong_dan_file = thu_muc_luu / ten_file
        
    tat_ca_cot = data[0].keys()
    
    with open(duong_dan_file, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=tat_ca_cot)
        writer.writeheader() 
        writer.writerows(data) 
        
    print(f"\n✅ Đã lưu toàn bộ chỉ số chi tiết vào file: {duong_dan_file}")

# --- HÀM CHÍNH: ĐIỀU PHỐI CÁC HÀM TRÊN ---
def main():
    parser = argparse.ArgumentParser(description="Công cụ tra cứu cầu thủ bóng đá")
    parser.add_argument("--name", help="Tên cầu thủ cần tra cứu")
    parser.add_argument("--club", help="Tên câu lạc bộ cần tra cứu")
    args = parser.parse_args()

    if not args.name and not args.club:
        print("Vui lòng nhập --name hoặc --club để tra cứu.")
        return

    print(f"Đang tìm kiếm thông tin ...")
    
    # BƯỚC 1: Lấy dữ liệu
    data = fetch_player_data(args.name, args.club)
    

    if data and len(data) > 0:
        display_table(data)
        save_to_csv(data, args)
    elif data is not None and len(data) == 0:
        print("❌ API trả về thành công nhưng không có dữ liệu (Danh sách rỗng).")

if __name__ == "__main__":
    main()