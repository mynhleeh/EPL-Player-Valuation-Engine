from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.dummy import DummyRegressor
from xgboost import XGBRegressor
import pandas as pd
import numpy as np

from core.config import OUTPUTS_PATH, TEST_SIZE, RANDOM_STATE, BASE_XGB_PARAMS, EARLY_STOPPING_ROUNDS
from core.loader import get_merged_data
from core.features import prepare_features
from core.training import train_model
from core.charts import plot_comparison, plot_importance, plot_residuals


def get_metrics(y_test: np.ndarray, y_pred: np.ndarray) -> list[float]:
    y_test = np.expm1(y_test)
    y_pred = np.expm1(y_pred)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return [rmse, mae, r2]


def run_evaluation(best_params: dict, x_train, y_train, x_test, y_test, player_test) -> None:
    cmp_dummy_xgb = pd.DataFrame({'Metrics': ['rmse', 'mae', 'r2']})

    # Dummy Regressor
    dummy = DummyRegressor(strategy="mean")
    dummy.fit(x_train, y_train)
    dummy_y_pred = dummy.predict(x_test)
    cmp_dummy_xgb["Dummy_Regressor"] = get_metrics(y_test, dummy_y_pred)

    # XGB Regressor
    final_params = {**BASE_XGB_PARAMS, **best_params}
    x_tr, x_val, y_tr, y_val = train_test_split(
        x_train, y_train, test_size=0.15, random_state=RANDOM_STATE
    )
    
    final_model = XGBRegressor(**final_params, early_stopping_rounds=EARLY_STOPPING_ROUNDS)
    final_model.fit(x_tr, y_tr, eval_set=[(x_val, y_val)], verbose=False)
    y_pred = final_model.predict(x_test)

    # Export Compare dummy vs xgb Regressor
    cmp_dummy_xgb['XGB_Regressor'] = get_metrics(y_test, y_pred)
    cmp_dummy_xgb.to_excel(str(OUTPUTS_PATH / "compare_dummy_xgb.xlsx"), index=False)
    cmp_dummy_xgb.to_csv(str(OUTPUTS_PATH / "compare_dummy_xgb.csv"), index=False)

    # Export Test
    actual_prices = np.expm1(y_test)
    predicted_prices = np.expm1(y_pred)

    test_stat = pd.DataFrame({
        'Player': player_test,
        'Actual_Transfer_Value_M': actual_prices,
        'Predicted_Value_M': predicted_prices,
        'Residual_Error': actual_prices - predicted_prices,
        'Valuation_Status': np.select(
            [predicted_prices > actual_prices, predicted_prices < actual_prices],
            ['Undervalued', 'Overvalued'],
            default='Fair Valued'
        )
    })

    test_stat['Abs_Error'] = test_stat['Residual_Error'].abs()
    test_stat = test_stat.sort_values(by='Abs_Error', ascending=False).drop(columns=['Abs_Error'])
    test_stat.to_excel(str(OUTPUTS_PATH / "player_valuation_results.xlsx"), index=False)
    test_stat.to_csv(str(OUTPUTS_PATH / "player_valuation_results.csv"), index=False)

    # Charts
    plot_comparison(y_test, y_pred)
    plot_importance(final_model.feature_importances_, x_test.columns)
    plot_residuals(y_test, y_pred)


if __name__ == '__main__':
    df = prepare_features(get_merged_data())
    player = df['Player']

    y = np.log1p(df['transfer'])
    x = df.drop(columns=['transfer', 'Player'])

    x_train, x_test, y_train, y_test, player_train, player_test = train_test_split(
        x, y, player, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    name, db_url = "params", f"sqlite:///{OUTPUTS_PATH}/params_trial.db"
    study = train_model(name, db_url, x_train, y_train)

    run_evaluation(study.best_params, x_train, y_train, x_test, y_test, player_test)
