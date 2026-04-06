from flask import Flask, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)

# Hàm hỗ trợ kết nối database chuyên nghiệp hơn
def get_db_connection():
    # --- PHẦN ĐƯỢC SỬA ---
    # Lấy đường dẫn thư mục hiện tại (part2)
    current_dir = Path(__file__).parent
    # Lùi 2 cấp về thư mục gốc, rồi trỏ vào thư mục data
    db_path = current_dir.parent.parent / 'data' / 'database.db'
    
    # Kết nối bằng đường dẫn động
    conn = sqlite3.connect(db_path)
    # -----------------------
    
    # Dòng này rất quan trọng: Giúp kết quả trả về có chứa tên cột
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/api/players', methods=['GET'])
def search_player_stats():
    # 1. Lấy tham số tìm kiếm từ đường dẫn
    name = request.args.get('name')
    club = request.args.get('club')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 2. Viết câu lệnh truy vấn vào bảng 'statistic'
    query = "SELECT * FROM statistic WHERE 1=1"
    params = []
    
    # Nếu có tìm theo tên, so sánh với cột 'Player'
    if name:
        query += " AND Player LIKE ?"
        params.append(f"%{name}%")
        
    # Nếu có tìm theo câu lạc bộ, so sánh với cột 'Squad'
    if club:
        query += " AND Squad LIKE ?"
        params.append(f"%{club}%")
        
    # 3. Thực thi và lấy dữ liệu
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # 4. Chuyển đổi dữ liệu thành dạng danh sách từ điển (list of dicts) để tạo JSON chuẩn
    results = [dict(row) for row in rows]
    
    # Trả về kết quả
    if not results:
        return jsonify({"message": "Không tìm thấy cầu thủ nào phù hợp."}), 404
        
    return jsonify(results)

if __name__ == '__main__':
    # Bật debug=True để tự động cập nhật khi bạn sửa code
    app.run(port=5000, debug=True)