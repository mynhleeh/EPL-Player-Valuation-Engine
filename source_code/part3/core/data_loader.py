import pandas as pd
import sqlite3

from .config import DATA_PATH


def fetch_database() -> pd.DataFrame:
    with sqlite3.connect(str(DATA_PATH / "database.db")) as conn:
        query = """
        SELECT stat.*, p.price as transfer
        FROM statistic as stat
        LEFT JOIN price p
        ON stat.Player = p.Player
        """
        df = pd.read_sql(query, conn)

    print("Fetched Database Successfully")
    return df


def load_and_merge() -> pd.DataFrame:
    db = fetch_database()
    analysis = pd.read_csv(str(DATA_PATH / "analysis.csv"))
    merged = pd.merge(left=db, right=analysis, on='Squad', how='left')
    
    return merged