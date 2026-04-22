from pathlib import Path
import pandas as pd
import sqlite3


path = Path(__file__).resolve().parent.parent.parent / "data"

def calculate_stats():
    with sqlite3.connect(str(path / "database.db")) as conn:
        df = pd.read_sql("SELECT * FROM statistic", conn)

        cols = ['Age', 'MP', 'Starts', 'Min', '90s', 'Gls_perf', 'Ast_perf', 'G+A_perf',
                'G-PK_perf', 'PK_perf', 'PKatt_perf', 'CrdY_perf', 'CrdR_perf', 'Gls_per90',
                'Ast_per90', 'G+A_per90', 'G-PK_per90', 'G+A-PK_per90']
        
        table = df.groupby('Squad')[cols].agg(['median', 'mean', 'std'])
        table.columns = [f"{col}_{stat}" for col, stat in table.columns]
        
        table = table.reset_index()
        return table


def get_max_stats(df: pd.DataFrame):
    table = pd.DataFrame()

    table['Stat'] = [c for c in df.columns]
    table['Squad'] = [df[s].idxmax() for s in table['Stat']]
    table['Max_Value'] = [df[s].max() for s in table['Stat']]

    table = table.drop(table.index[0])
    return table


def rank_squads(data: pd.DataFrame):
    ref = pd.DataFrame()

    ref['stat'] = ['G+A_per90_mean', 'G-PK_per90_mean', 'G+A_perf_median',
                   'Gls_per90_std', 'CrdR_perf_mean', 'CrdY_perf_mean', 'Min_std']
    ref['prop'] = [1, 1, 1, -1, -1, -1, -1]
    ref['wei'] = [0.25, 0.2, 0.15, 0.1, 0.12, 0.08, 0.1]

    df = pd.DataFrame()
    df['Squad'] = data['Squad']

    for s, p, w in zip(ref['stat'], ref['prop'], ref['wei']):
        min_val, max_val = data[s].min(), data[s].max()
        
        if p == 1: val = (data[s] - min_val) / (max_val - min_val)
        else: val = (max_val - data[s]) / (max_val - min_val)

        df[s] = val * w

    df['Sum'] = df.drop(columns=['Squad']).sum(axis=1) * 100
    df = df.sort_values(by="Sum", ascending=False).reset_index(drop=True)
    
    return df


if __name__ == '__main__':
    new_stat = calculate_stats()
    new_stat.to_csv(str(path / "squad_stats_summary.csv"), index=False)
    print("Exported csv successfully")

    max_stat = get_max_stats(new_stat)
    print("Teams with highest statistics:")
    print(max_stat)

    rank = rank_squads(new_stat)
    print("Based on multivariate evaluation model (Offense, technique, stability,...)")
    print(f"The most impressive team in the league is {rank['Squad'][0]}")
