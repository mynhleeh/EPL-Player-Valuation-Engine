import pandas as pd
import numpy as np


def processing(df: pd.DataFrame) -> pd.DataFrame:
    # Set-up main features
    cols = ['Player', 'Squad', 'Nation', 'transfer', 'Age', 'Min', 'Gls_perf', 'Ast_perf',
            'PK_perf', 'CrdY_perf', 'CrdR_perf']
    
    # Set Category
    df['Nation'] = df['Nation'].astype('category')
    df['Squad'] = df['Squad'].astype('category')
    
    # Transfer process
    price = df['transfer'].replace("N/A", np.nan)
    price = price.str.replace('[€M]', '', regex=True)
    price = pd.to_numeric(price, errors='coerce')
    df['transfer'] = price

    # One-Hot Encoding
    dummies = df['Pos'].str.get_dummies(sep=',')
    df = pd.concat([dummies, df], axis=1)
    cols += list(dummies.columns)
    
    # New features only db
    df['Squad_Status'] = np.where(df['MP'] != 0, df['Starts'] / df['MP'], 0)
    df['Stamina_Trust'] = np.where(df['MP'] != 0, df['Min'] / df['MP'], 0)
    df['NPG_Efficiency'] = np.where(df['Min'] != 0, (df['Gls_perf'] - df['PK_perf']) / df['Min'], 0)
    df['Discipline_Risk'] = np.where(df['Min'] != 0, (df['CrdY_perf'] + 2 * df['CrdR_perf']) / df['Min'], 0)
    df['Assist_Efficiency'] = np.where(df['Min'] != 0, df['Ast_perf'] / df['Min'], 0)

    cols += ['Squad_Status', 'Stamina_Trust', 'NPG_Efficiency', 'Discipline_Risk', 'Assist_Efficiency']
    
    # New features include analysis.csv
    df['Min_Z_Score'] = np.where(df['Min_std'] != 0, (df['Min'] - df['Min_mean']) / df['Min_std'] , 0)
    df['Age_Diff_Squad'] = df['Age'] - df['Age_mean']
    df['Offensive_Share_Proxy'] = (df['Gls_perf'] + df['Ast_perf']) / (df['G+A_perf_mean'] + 1e-5)
    df['Squad_Age_Profile'] = df['Age_mean']
    df['Squad_Rotation_Index'] = df['Min_std']
    df['Squad_Discipline'] = df['CrdY_perf_mean'] + df['CrdR_perf_mean']

    cols += ['Min_Z_Score', 'Age_Diff_Squad', 'Offensive_Share_Proxy', 'Squad_Age_Profile',
             'Squad_Rotation_Index', 'Squad_Discipline']

    df = df.loc[:, cols]
    df = df.dropna(subset='transfer').reset_index(drop=True)

    print("Processed Data Successfully")
    return df
