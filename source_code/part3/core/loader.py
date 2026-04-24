import pandas as pd
import sqlite3

from .config import DATA_PATH


def get_raw_data() -> pd.DataFrame:
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


def get_merged_data() -> pd.DataFrame:
    db = get_raw_data()
    analysis = pd.read_csv(str(DATA_PATH / "squad_stats_summary.csv"))
    merged = pd.merge(left=db, right=analysis, on='Squad', how='left')
    
    return merged
