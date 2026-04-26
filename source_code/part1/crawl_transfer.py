import sqlite3
import urllib.parse
from pathlib import Path
from seleniumbase import SB
from thefuzz import fuzz


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
    conn.execute("DROP TABLE IF EXISTS price")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS price "
        "(Player TEXT UNIQUE, Price TEXT)"
    )
    conn.commit()


def fetch_val(sb, name: str):
    # Build search URL with URL-encoded player name
    url = f"https://www.footballtransfers.com/en/search?search_value={urllib.parse.quote(name)}"
    sb.uc_open_with_reconnect(url)

    # Wait for player search results
    try: sb.wait_for_element("a.playerList-box", timeout=12)
    except Exception: return "N/a"

    # Get best matched player
    best_box, highest_score = None, 0
    boxes = sb.find_elements("a.playerList-box")
    
    for box in boxes:
        # Get player title
        title = box.get_attribute("title")
        if not title: continue

        # Calculate similarity score
        score = fuzz.token_sort_ratio(name.lower(), title.strip().lower())
        if score > highest_score:
            highest_score = score
            best_box = box

            if score == 100: break

    # Extract market value
    if best_box is not None and highest_score > 80:
        tags = best_box.find_elements("css selector", "span.player-tag")
        if tags: return tags[0].text.strip()

    return "N/a"


if __name__ == "__main__":
    db_path = Path(__file__).resolve().parents[2] / "data" / "database.db"

    # Load all player names
    all_names = all_players(db_path)
    total = len(all_names)

    with sqlite3.connect(str(db_path)) as conn:
        # Setup price table
        price_table(conn)

        # Get existing players
        existing = exist_players(conn)
        pending = [name for name in all_names if name not in existing]
        remaining = len(pending)

        # Print progress
        if remaining < total:
            print(f"Resuming: {total - remaining}/{total} done, {remaining} remaining")

        # Crawl player prices
        with SB(uc=True, headless=True) as sb:
            for count, name in enumerate(pending, start=1):
                # Fetch player price
                val = fetch_val(sb, name)
                print(f"[{count}/{remaining}] {name}: {val}")

                # Insert player price
                conn.execute(
                    "INSERT OR IGNORE INTO price (Player, Price) VALUES (?, ?)",
                    (name, val),
                )

                # Commit every 25 players
                if count % 25 == 0: conn.commit()

        conn.commit()
    print("Finished crawling player prices")