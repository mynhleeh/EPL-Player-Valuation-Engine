import seleniumbase
import pandas as pd
import numpy as np
import sqlite3
import io

from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def fetch_stats(url):
    driver = seleniumbase.Driver(uc=True)

    driver.uc_open_with_reconnect(url)
    # driver.uc_gui_click_captcha()

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "div_stats_standard"))
    )

    table = pd.read_html(io.StringIO(driver.page_source))
    driver.quit()

    print("Finish Web Scraping")
    return table[-1]


def format_stats(df: pd.DataFrame):
    cols = []
    for a, b in df.columns:
        if a == 'Performance': cols.append(f"{b}_perf")
        elif '90' in a: cols.append(f"{b}_per90")
        else: cols.append(b)

    if isinstance(df.columns, pd.MultiIndex): df.columns = cols
    df = df[df.iloc[:, 0] != 'Rk'].copy()

    print('Reformat Data Successful')
    return df
    
    
def clean_stats(data):
    # Filter
    data["Min"] = pd.to_numeric(data["Min"], errors='coerce')
    data.query("Min > 90", inplace=True)

    # Format data type
    cols = ['Age', 'Born', 'MP', 'Starts', '90s', 'Gls_perf', 'Ast_perf', 'G+A_perf',
            'G-PK_perf', 'PK_perf', 'PKatt_perf', 'CrdY_perf', 'CrdR_perf', 'Gls_per90',
            'Ast_per90', 'G+A_per90', 'G-PK_per90', 'G+A-PK_per90']
    for c in cols: data[c] = pd.to_numeric(data[c], errors='coerce')

    print("Finish Clean Data")


def save_stats(data: pd.DataFrame):
    base_dir = Path(__file__).resolve().parent.parent.parent
    path = str(base_dir / "data" / "database.db")

    conn = sqlite3.connect(path)

    # data = data.fillna('N/a')
    data.to_sql('statistic', conn, if_exists='replace', index=False)
    conn.close()

    print("Exported to SQL")


if __name__ == '__main__':
    url = "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats"
    table = fetch_stats(url)
    
    table = format_stats(table)
    clean_stats(table)
    save_stats(table)
