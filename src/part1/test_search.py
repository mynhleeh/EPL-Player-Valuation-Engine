import re
import urllib.parse
from seleniumbase import SB
import random

players_db = ["Cole Palmer", "Martin Ødegaard"]

with SB(uc=True, headless=True) as sb:
    for player in players_db:
        try:
            clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', player)
            query = urllib.parse.quote(clean_name)
            
            search_url = f"https://www.footballtransfers.com/en/search?search_value={query}"
            print("Opening:", search_url)
            sb.open(search_url)
            sb.sleep(random.uniform(2, 4))
            
            if sb.is_element_visible("a.player-tag", timeout=3):
                print("Found player-tag!")
                sb.click("a.player-tag")
                sb.sleep(random.uniform(1.5, 3))

            value = "N/a"
            if sb.is_element_present("span.etv-value", timeout=3):
                value = sb.get_text("span.etv-value").strip()
            
            print(f"-> {player}: {value}")
        except Exception as e:
            print("Error:", e)
