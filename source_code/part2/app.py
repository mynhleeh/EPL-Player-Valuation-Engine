from flask import Flask, request, jsonify, g
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.json.sort_keys = False 


def get_db_path():
    current_dir = Path(__file__).resolve().parent
    return current_dir.parent.parent / 'data' / 'database.db'


def get_db():
    # Manage DB connection per request
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(get_db_path())
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    # Auto-close DB connection after request
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/api/search', methods=['GET'])
def search_player_stats():
    # Query parameters
    name = request.args.get('name')
    club = request.args.get('club')
    
    if not name and not club:
        return jsonify({"error": "Please provide at least 'name' or 'club'."}), 400

    # Build base query for 'statistic' table
    query = "SELECT * FROM statistic WHERE 1=1"
    params = []
    
    # Filter by name
    if name:
        query += " AND Player LIKE ?"
        params.append(f"%{name}%")
        
    # Filter by club
    if club:
        query += " AND Squad LIKE ?"
        params.append(f"%{club}%")
        
    # Execute query using the managed connection
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    
    if not results:
        return jsonify({"message": "No matching data found."}), 404
        
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=5000, debug=True)