from pathlib import Path
import seleniumbase
import pandas as pd
import sqlite3
import io

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def fetch_stats(url):
    with seleniumbase.Driver(uc=True) as driver:
        driver.uc_open_with_reconnect(url)
        # driver.uc_gui_click_captcha()

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "div_stats_standard"))
        )

        print("Successfully fetched HTML data from the website.")
        return driver.page_source


def format_stats(html):
    df = pd.read_html(io.StringIO(html), attrs={'id': 'stats_standard'})[0]
    df = df[df.iloc[:, 1] != 'Player'].copy()

    new_cols = []
    for col in df.columns:
        lvl0 = str(col[0])
        lvl1 = str(col[1])

        if "Performance" in lvl0: new_cols.append(f"{lvl1}_perf")
        elif "Per 90" in lvl0: new_cols.append(f"{lvl1}_per90")
        else: new_cols.append(lvl1)
            
    df.columns = new_cols
    return df.iloc[:, :25]


def clean_data(df):
    # Convert data types.
    exc = ['Player', 'Nation', 'Pos', 'Squad', 'Matches']
    fix = [c for c in df.columns if c not in exc]
    df[fix] = df[fix].apply(pd.to_numeric, errors='coerce')

    # Filter players >90 minutes.
    if 'Min' in df.columns: df = df[df['Min'] > 90].reset_index(drop=True)

    # Remove duplicates.
    df.drop_duplicates(subset='Player', keep='first', inplace=True)
    return df


def save_to_statistic_table(df, path):
    with sqlite3.connect(path) as conn:
        df.to_sql("statistic", conn, if_exists="replace", index=False)
        print("Successfully saved data to the database.")


if __name__ == "__main__":
    url = "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats"
    html = fetch_stats(url)
    
    df = format_stats(html)
    df = clean_data(df)

    path = Path(__file__).resolve().parents[2] / "data" / "database.db"
    save_to_statistic_table(df, path)