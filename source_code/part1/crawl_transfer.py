import sqlite3
import urllib.parse
from pathlib import Path
from seleniumbase import SB
from thefuzz import fuzz

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "database.db"


def get_names(path):
    # Load player names.
    with sqlite3.connect(str(path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Player FROM statistic")
        return [row[0] for row in cursor.fetchall()]


def fetch_val(sb, name):
    # Fetch transfer value.
    url = f"https://www.footballtransfers.com/en/search?search_value={urllib.parse.quote(name)}"
    sb.open(url)
    
    # Wait for results.
    for _ in range(16):
        if sb.is_element_present("a.playerList-box"):
            break
        sb.sleep(0.5)
    else:
        return "N/a"

    boxes = sb.find_elements("a.playerList-box")
    best_title = None
    highest_score = 0

    # Find closest name match.
    for b in boxes:
        title = b.get_attribute("title")
        if not title:
            continue
        score = fuzz.token_sort_ratio(name.lower(), title.strip().lower())
        if score > highest_score:
            highest_score = score
            best_title = title.strip()
    
    # Process valid matches.
    if best_title and highest_score > 80:
        # Extract transfer price.
        safe_title = best_title.replace('"', '\\"')
        css_selector = f'a[title="{safe_title}"] span.player-tag'
        if sb.is_element_present(css_selector):
            return sb.get_text(css_selector).strip()
    
    return "N/a"


def setup_price_table(conn):
    # Setup price table.
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS price")
    cursor.execute("CREATE TABLE price (Player TEXT, Price TEXT)")
    conn.commit()


if __name__ == "__main__":
    all_names = get_names(DB_PATH)
    
    with sqlite3.connect(str(DB_PATH)) as conn:
        setup_price_table(conn)

        with SB(uc=True, headless=True) as sb:
            # Iterate all players.
            for index, n in enumerate(all_names):
                val = fetch_val(sb, n)
                print(f"{index}. {n}: {val}")
                
                # Insert data immediately.
                conn.execute("INSERT INTO price (Player, Price) VALUES (?, ?)", (n, val))
        
        # Commit after loop.
        conn.commit()