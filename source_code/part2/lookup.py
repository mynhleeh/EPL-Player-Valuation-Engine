import requests
import argparse
import csv
from tabulate import tabulate
from pathlib import Path

API_URL = "http://127.0.0.1:5000/api/search"

def fetch_player_data(name, club):
    params = {}
    if name: params['name'] = name
    if club: params['club'] = club

    response = requests.get(API_URL, params=params)

    if response.ok:
        return response.json()
    
    print("Không tìm thấy dữ liệu phù hợp.")
    return None

def display_table(data):
    
    table_data = [
        [row.get('Player'), row.get('Squad'), row.get('Nation'), row.get('Pos'), row.get('Age')]
        for row in data
    ]
    headers = ["NAME", "CLUB", "NATION", "POS", "AGE"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def save_to_csv(data, args):
    out_dir = Path(__file__).parent.parent / 'data' / 'lookup_ans'
    out_dir.mkdir(parents=True, exist_ok=True) 

    # Logic đặt tên file dựa trên tham số tìm kiếm
    file_parts = [p.replace(' ', '_') for p in [args.name, args.club] if p]
    file_name = f"{'_'.join(file_parts)}.csv"
    file_path = out_dir / file_name
        
    with open(file_path, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader() 
        writer.writerows(data) 
        
    print(f"\n Đã lưu toàn bộ chỉ số chi tiết vào file: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Công cụ tra cứu cầu thủ bóng đá")
    parser.add_argument("--name", help="Tên cầu thủ cần tra cứu")
    parser.add_argument("--club", help="Tên câu lạc bộ cần tra cứu")
    args = parser.parse_args()

    if not args.name and not args.club:
        parser.error("Vui lòng nhập --name hoặc --club để tra cứu.")

    print("Đang tìm kiếm thông tin ...")
    
    if data := fetch_player_data(args.name, args.club):
        display_table(data)
        save_to_csv(data, args)

if __name__ == "__main__":
    main()