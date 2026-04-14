from flask import Flask, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)


def get_db_path():
    current_dir = Path(__file__).parent
    return current_dir.parent.parent / 'data' / 'database.db'

@app.route('/api/search', methods=['GET'])
def search_player_stats():
    # Lấy tham số tìm kiếm từ đường dẫn
    name = request.args.get('name')
    club = request.args.get('club')
    
    if not name and not club:
        return jsonify({"error": "Vui lòng cung cấp ít nhất 'name' hoặc 'club'."}), 400

    # Truy vấn vào bảng 'statistic'
    query = "SELECT * FROM statistic WHERE 1=1"
    params = []
    
    # Tìm theo tên
    if name:
        query += " AND Player LIKE ?"
        params.append(f"%{name}%")
        
    # Tìm theo câu lạc bộ
    if club:
        query += " AND Squad LIKE ?"
        params.append(f"%{club}%")
        
    db_path = get_db_path()

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
    
    if not results:
        return jsonify({"message": "Không tìm thấy dữ liệu phù hợp."}), 404
        
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=5000, debug=True)