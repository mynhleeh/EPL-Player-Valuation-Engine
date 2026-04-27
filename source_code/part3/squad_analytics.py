from pathlib import Path
import pandas as pd
import sqlite3

path = Path(__file__).resolve().parent.parent.parent / "data"

def calculate_stats():
    # Select columns
    cols = [
        'Age', 'MP', 'Starts', 'Min', '90s', 'Gls_perf', 'Ast_perf', 'G+A_perf',
        'G-PK_perf', 'PK_perf', 'PKatt_perf', 'CrdY_perf', 'CrdR_perf', 'Gls_per90',
        'Ast_per90', 'G+A_per90', 'G-PK_per90', 'G+A-PK_per90'
    ]
    
    # Load stats
    with sqlite3.connect(str(path / "database.db")) as conn:
        query = ", ".join([f'"{c}"' for c in (['Squad'] + cols)])
        df = pd.read_sql(f"SELECT {query} FROM statistic", conn)

    # Calculate
    table = df.groupby('Squad')[cols].agg(['median', 'mean', 'std'])
    table.columns = [f"{col}_{stat}" for col, stat in table.columns]
    
    return table.reset_index()


def get_max_stats(df: pd.DataFrame):
    # Set Squad as index
    numeric_df = df.set_index('Squad')
    
    # Calculate max values
    max_values = numeric_df.max()
    max_squads = numeric_df.idxmax()
    
    # Create dataframe
    result = pd.DataFrame({
        'Stat': max_values.index,
        'Squad': max_squads.values,
        'Max_Value': max_values.values
    })
    
    return result


def rank_squads(data: pd.DataFrame):
    # Evaluation criteria configuration
    ref = pd.DataFrame({
        'stat': ['G+A_per90_mean', 'G-PK_per90_mean', 'G+A_perf_median',
                 'Gls_per90_std', 'CrdR_perf_mean', 'CrdY_perf_mean', 'Min_std'],
        'prop': [1, 1, 1, -1, -1, -1, -1],
        'wei': [0.25, 0.2, 0.15, 0.1, 0.12, 0.08, 0.1]
    })

    # Calculate stats
    df = pd.DataFrame({'Squad': data['Squad']})
    for _, row in ref.iterrows():
        s, p, w = row['stat'], row['prop'], row['wei']

        min_val, max_val = data[s].min(), data[s].max()
        denom = max_val - min_val
        
        if denom == 0: val = 0.0
        else:
            if p == 1: val = (data[s] - min_val) / denom
            else: val = (max_val - data[s]) / denom

        df[s] = val * w

    # Calculate final score (percentage)
    df['Score'] = df.drop(columns=['Squad']).sum(axis=1) * 100
    
    # Sort by score descending
    df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
    
    return df


if __name__ == '__main__':
    # Squad stats summary
    squad_stats = calculate_stats()
    squad_stats.to_csv(str(path / "squad_stats_summary.csv"), index=False)
    print("Exported optimized csv successfully")

    # Find maximums
    max_stats_summary = get_max_stats(squad_stats)
    print("Teams with highest statistics:")
    print(max_stats_summary) 

    # Rank squads
    rankings = rank_squads(squad_stats)
    print("Based on multivariate evaluation model (Offense, technique, stability,...)")
    
    best_team = rankings.iloc[0]
    print(f"The most impressive team in the league is: "
            f"{best_team['Squad']} (Score: {best_team['Score']:.2f})")