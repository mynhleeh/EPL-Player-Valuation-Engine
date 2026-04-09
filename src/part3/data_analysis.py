from pathlib import Path
import pandas as pd
import sqlite3


base_dir = Path(__file__).resolve().parent.parent.parent
path = base_dir / "data"

def calculate_stat():
    with sqlite3.connect(str(path / "database.db")) as conn:
        df = pd.read_sql("SELECT * FROM statistic", conn)

        cols = ['Age', 'MP', 'Starts', 'Min', '90s', 'Gls_perf', 'Ast_perf', 'G+A_perf',
                'G-PK_perf', 'PK_perf', 'PKatt_perf', 'CrdY_perf', 'CrdR_perf', 'Gls_per90',
                'Ast_per90', 'G+A_per90', 'G-PK_per90', 'G+A-PK_per90']
        
        table = df.groupby('Squad')[cols].agg(['median', 'mean', 'std'])
        table.columns = [f"{col}_{stat}" for col, stat in table.columns]
        return table


def find_stat(df: pd.DataFrame):
    table = pd.DataFrame()

    table['Stat'] = [c for c in df.columns]
    table['Squad'] = [df[s].idxmax() for s in table['Stat']]
    table['Max_Value'] = [df[s].max() for s in table['Stat']]
    return table


if __name__ == '__main__':
    new_stat = calculate_stat()
    new_stat.to_csv(str(path / "analysis.csv"))
    print("Exported csv successfully")

    max_stat = find_stat(new_stat)
    print("Đội bóng có các chỉ số cao nhất:")
    print(max_stat)