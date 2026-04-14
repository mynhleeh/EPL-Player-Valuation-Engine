from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.model_selection import RepeatedKFold, StratifiedKFold, RepeatedStratifiedKFold
from sklearn.metrics import r2_score
from xgboost import XGBRegressor
from pathlib import Path
import pandas as pd
import numpy as np
import sqlite3
import optuna

path = Path(__file__).resolve().parent.parent.parent / "data"

def fetch_database():
    with sqlite3.connect(str(path / "database.db")) as conn:
        query = """
        SELECT stat.*, p.price as transfer
        FROM statistic as stat
        LEFT JOIN price p
        ON stat.Player = p.Player
        """
        df = pd.read_sql(query, conn)

        print("Fetched Database Successfully")
        return df


def processing(df: pd.DataFrame):
    # Set-up main features
    cols = ['Squad', 'Nation', 'transfer', 'Age', 'Min', 'Gls_perf', 'Ast_perf',
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
    cols += [c for c in dummies.columns]
    
    # New features only db
    df['Squad_Status'] = np.where(df['MP'] != 0, df['Starts'] / df['MP'], 0)
    df['Stamina_Trust'] = np.where(df['MP'] != 0, df['Min'] / df['MP'], 0)
    df['NPG_Efficiency'] = np.where(df['Min'] != 0, (df['Gls_perf'] - df['PK_perf']) / df['Min'], 0)
    df['Discipline_Risk'] = np.where(df['Min'] != 0, (df['CrdY_perf'] + 2 * df['CrdR_perf']) / df['Min'], 0)
    df['Assist_Efficiency'] = df['Ast_perf'] / df['Min']

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
    df.dropna(subset='transfer', inplace=True, ignore_index=True)

    print("Processed Data Succesfully")
    return df


def objective(trial, x, y):
    param = {
        'enable_categorical': True,
        'n_jobs': -1,
        'learning_rate': trial.suggest_float('learning_rate', 0.001, 1.0),
        'min_split_loss': trial.suggest_float('min_split_loss', 0, 10000),
        'alpha': trial.suggest_float('alpha', 1e-8, 1.0),
        'lambda': trial.suggest_float('lambda', 1e-8, 1.0),
        'max_depth': trial.suggest_int('max_depth', 3, 7),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
    }

    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)
    y_binned = pd.qcut(y, q=10, labels=False, duplicates='drop')

    model = XGBRegressor(**param)
    score = []

    for train, val in cv.split(x, y_binned):
        x_train, x_val = x.iloc[train], x.iloc[val]
        y_train, y_val = y.iloc[train], y.iloc[val]

        model.fit(x_train, y_train, eval_set=[(x_val, y_val)], verbose=False)
        scr = r2_score(y_val, model.predict(x_val))

        score.append(scr)
    return np.mean(score)


def try_params(x: pd.DataFrame, y: pd.DataFrame, name: str, url: str):
    func = lambda trial: objective(trial, x, y)

    study = optuna.create_study(
        study_name=name,
        storage=url,
        load_if_exists=True,
        sampler=optuna.samplers.CmaEsSampler(),
        direction='maximize'
    )
    study.optimize(func, n_trials=10000, gc_after_trial=True, show_progress_bar=True)


def train_best_params(x, y, name: str, url: str):
    param = {
        'enable_categorical': True,
        'n_jobs': -1,
    }

    best_param = optuna.load_study(study_name=name, storage=url).best_params
    for k, v in best_param.items():
        if k not in param: param[k] = v

    model = XGBRegressor(**param)
    # model.fit(x_train, y_train)

    # score = model.score(x_test, y_test)
    # print(score)


def train_model(df: pd.DataFrame):
    name, db_url = "params", f"sqlite:///{path}/params_trial.db"

    y = np.log1p(df['transfer'])
    x = df.drop(columns='transfer')
    
    try_params(x, y, name, db_url)
    # train_best_params(x, y, name, db_url)

if __name__ == '__main__':
    db = fetch_database()
    analysis = pd.read_csv(str(path / "analysis.csv"))

    merged = pd.merge(left=db, right=analysis, on='Squad', how='left')
    df = processing(merged)

    train_model(df)