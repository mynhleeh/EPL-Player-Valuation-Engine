import sqlite3
import urllib.parse
from pathlib import Path
from seleniumbase import SB
from thefuzz import fuzz


# Load player names
def all_players(path: Path):
    with sqlite3.connect(str(path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Player FROM statistic ORDER BY rowid")
        return [row[0] for row in cursor.fetchall()]


def exist_players(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Player FROM price")
    return {row[0] for row in cursor.fetchall()}


def price_table(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS price "
        "(stat_order INTEGER, Player TEXT UNIQUE, Price TEXT)"
    )
    conn.commit()


def fetch_val(sb, name: str):
    url = f"https://www.footballtransfers.com/en/search?search_value={urllib.parse.quote(name)}"
    sb.uc_open_with_reconnect(url)

    try: sb.wait_for_element("a.playerList-box", timeout=12)
    except Exception: return "N/a"

    best_box, highest_score = None, 0
    boxes = sb.find_elements("a.playerList-box")
    
    for box in boxes:
        title = box.get_attribute("title")
        if not title: continue

        score = fuzz.token_sort_ratio(name.lower(), title.strip().lower())
        if score > highest_score:
            highest_score = score
            best_box = box

            if score == 100: break

    if best_box is not None and highest_score > 80:
        tags = best_box.find_elements("css selector", "span.player-tag")
        if tags: return tags[0].text.strip()

    return "N/a"


if __name__ == "__main__":
    db_path = Path(__file__).resolve().parents[2] / "data" / "database.db"

    all_names = all_players(db_path)
    total = len(all_names)

    with sqlite3.connect(str(db_path)) as conn:
        price_table(conn)
        existing = exist_players(conn)

        pending = [
            (i, name) for i, name in enumerate(all_names)
            if name not in existing
        ]
        remaining = len(pending)

        if remaining < total:
            print(f"Resuming: {total - remaining}/{total} done, {remaining} remaining")

        with SB(uc=True, headless=True) as sb:
            for count, (order, name) in enumerate(pending, start=1):
                val = fetch_val(sb, name)
                print(f"[{count}/{remaining}] {name}: {val}")

                conn.execute(
                    "INSERT OR IGNORE INTO price (stat_order, Player, Price) VALUES (?, ?, ?)",
                    (order, name, val),
                )
                if count % 25 == 0: conn.commit()

        conn.commit()
    print("Done.")