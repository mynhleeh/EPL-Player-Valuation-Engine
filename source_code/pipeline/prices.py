from seleniumbase import Driver
from thefuzz import fuzz
from pathlib import Path
import sqlite3
import bs4

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def load_players(db_name):
    base_dir = Path(__file__).resolve().parent.parent.parent
    path = str(base_dir / "data" / db_name)

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT Player FROM statistic")

        print("Load players successfully")
        return list(e[0] for e in cur.fetchall())


def search_players(driver, player):
    url = f"https://www.footballtransfers.com/en/search?search_value={player}"
    driver.uc_open_with_reconnect(url)

    soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
    players_list = soup.find_all('a', class_='playerList-box')

    return players_list


def extract_price(players, target):
    for p in players:
        cur_player = p.find('strong').get_text()

        if fuzz.token_sort_ratio(cur_player, target) >= 85:
            price = p.find('span', class_='player-tag')
            return price.get_text()
    return "N/A"


def collect_prices(players, db_name):
    base_dir = Path(__file__).resolve().parent.parent.parent
    path = str(base_dir / "data" / db_name)

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    
    cur.execute("DROP TABLE IF EXISTS price")
    cur.execute('''
        CREATE TABLE price (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT,
            price TEXT
        )
    ''')

    print("Created new Table")
    driver = Driver(uc=True)

    for i in range(len(players)):
        print(f"Searching {players[i]}")
        price = extract_price(search_players(driver, players[i]), players[i])
    
        cur.execute("INSERT INTO price (player, price) VALUES (?, ?)", (players[i], price))
        print(f"Inserted {(players[i], price)}")
    
    driver.quit()
    conn.commit()
    conn.close()
    print("Collect price successfully")


if __name__ == '__main__':
    players = load_players("database.db")
    collect_prices(players, "database.db")
