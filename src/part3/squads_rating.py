import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent.parent
path = base_dir / "data"

def squads_ranking(data: pd.DataFrame):
    ref = pd.DataFrame()

    ref['stat'] = ['G+A_per90minutes_mean', 'G-PK_per90minutes_mean', 'G+A_performance_median', 'Gls_per90minutes_std', 'CrdR_mean', 'CrdY_mean', 'Min_std']
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
    data = pd.read_csv(str(path / "analysis.csv"))
    data.fillna(0, inplace=True)

    df = squads_ranking(data)
    print("Dựa trên mô hình đánh giá tổng hợp đa biến (Tấn công, kỹ thuật, tính ổn định,...)")
    print(f"Đội bóng có phong độ ấn tượng nhất giải đấu là {df['Squad'][0]}")