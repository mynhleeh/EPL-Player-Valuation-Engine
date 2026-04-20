from flask import Flask, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)


def get_db_path():
    current_dir = Path(__file__).parent
    return current_dir.parent.parent / 'data' / 'database.db'

@app.route('/api/search', methods=['GET'])
def search_player_stats():
    # Pick up query parameters
    name = request.args.get('name')
    club = request.args.get('club')
    
    if not name and not club:
        return jsonify({"error": "Please provide at least 'name' or 'club'."}), 400

    # Access column 'statistic'
    query = "SELECT * FROM statistic WHERE 1=1"
    params = []
    
    # Find by name
    if name:
        query += " AND Player LIKE ?"
        params.append(f"%{name}%")
        
    # Find by club
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
        return jsonify({"message": "No matching data found."}), 404
        
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=5000, debug=True)