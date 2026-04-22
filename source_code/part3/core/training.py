from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
import pandas as pd
import numpy as np
import optuna

from .config import (
    BASE_XGB_PARAMS, N_SPLITS, N_REPEATS, RANDOM_STATE,
    EARLY_STOPPING_ROUNDS, STRATIFY_BINS,
)


def objective(trial, x: pd.DataFrame, y: pd.Series) -> float:
    tuned_params = {
        'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.5, log=True),
        'min_split_loss': trial.suggest_float('min_split_loss', 1e-4, 10.0, log=True),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-3, 100.0, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 100.0, log=True),
        'max_depth': trial.suggest_int('max_depth', 2, 7),
        'subsample': trial.suggest_float('subsample', 0.1, 1.0, log=True),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.1, 1.0, log=True),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 15),
        'max_bin': trial.suggest_categorical('max_bin', [32, 64, 128]),
        'max_cat_to_onehot': trial.suggest_int('max_cat_to_onehot', 2, 25),
        'max_cat_threshold': trial.suggest_int('max_cat_threshold', 1, 64),
        'objective': trial.suggest_categorical('objective', [
            'reg:squarederror', 
            'reg:pseudohubererror'
        ]),
    }

    if tuned_params['objective'] == 'reg:pseudohubererror':
        tuned_params['huber_slope'] = trial.suggest_float('huber_slope', 0.1, 5.0)

    params = {**BASE_XGB_PARAMS, **tuned_params}

    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE)
    y_binned = pd.qcut(y, q=STRATIFY_BINS, labels=False, duplicates='drop')

    scores = []
    for fold_train, fold_val in cv.split(x, y_binned):
        x_train, x_val = x.iloc[fold_train], x.iloc[fold_val]
        y_train, y_val = y.iloc[fold_train], y.iloc[fold_val]

        model = XGBRegressor(**params, early_stopping_rounds=EARLY_STOPPING_ROUNDS)
        model.fit(x_train, y_train, eval_set=[(x_val, y_val)], verbose=False)

        pred = model.predict(x_val)
        fold_rmse = -np.sqrt(mean_squared_error(y_val, pred))
        scores.append(fold_rmse)

    return np.mean(scores)


def train_model(name: str, db_url: str, x_train: pd.DataFrame, y_train: pd.Series) -> optuna.Study:
    study = optuna.create_study(
        study_name=name,
        storage=db_url,
        load_if_exists=True,
        direction='maximize'
    )

    print("Training Status: Starting Optuna optimization...")
    study.optimize(
        lambda trial: objective(trial, x_train, y_train),
        n_trials=1,
        gc_after_trial=True,
        show_progress_bar=True
    )

    return study