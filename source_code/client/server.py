from flask import Flask, request, jsonify, g
from pathlib import Path
import sqlite3

app = Flask(__name__)
app.json.sort_keys = False

base_dir = Path(__file__).resolve().parent.parent.parent
path = str(base_dir / "data" / "database.db")


def get_db():
    db = getattr(g, "_database", None)

    if db is None:
        db = g._database = sqlite3.connect(path)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None: db.close()


@app.route('/api/search', methods=['GET'])
def search_api():
    player = request.args.get('player')
    squad = request.args.get('squad')

    conn = get_db()
    cur = conn.cursor()

    if player:cur.execute("SELECT * FROM statistic WHERE Player LIKE ?", (f"%{player}%", ))
    elif squad: cur.execute("SELECT * FROM statistic WHERE Squad LIKE ?", (f"%{squad}%", ))
    else: return jsonify({"error": "Missing player or squad parameter"}), 400

    rows = cur.fetchall()
    if not rows: return jsonify({"error": "No data"})
    return jsonify([dict(r) for r in rows])


if __name__ == '__main__':
    app.run(debug=True)
