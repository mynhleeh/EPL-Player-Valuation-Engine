from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data"
OUTPUTS_PATH = DATA_PATH / "outputs"
CHARTS_PATH = DATA_PATH / "charts"
RANDOM_STATE = 42
TEST_SIZE = 0.2
N_SPLITS = 5
N_REPEATS = 3
N_ESTIMATORS = 1000
EARLY_STOPPING_ROUNDS = 50
STRATIFY_BINS = 10

MONOTONE_CONSTRAINTS = {
    'Age': 0, 'Min': 1, 'Gls_perf': 1, 'Ast_perf': 1, 'PK_perf': 1,
    'CrdY_perf': -1, 'CrdR_perf': -1, 'Squad_Status': 1, 'Stamina_Trust': 1,
    'NPG_Efficiency': 1, 'Discipline_Risk': -1, 'Assist_Efficiency': 1,
    'Min_Z_Score': 1, 'Age_Diff_Squad': 0, 'Offensive_Share_Proxy': 1,
    'Squad_Age_Profile': 0, 'Squad_Rotation_Index': 0, 'Squad_Discipline': 0
}

INTERACTION_CONSTRAINTS = [
    ['Gls_perf', 'Ast_perf', 'PK_perf', 'NPG_Efficiency',
     'Assist_Efficiency', 'Offensive_Share_Proxy'],
    ['Age', 'Min', 'Squad_Status', 'Stamina_Trust', 'Min_Z_Score'],
    ['CrdY_perf', 'CrdR_perf', 'Discipline_Risk', 'Squad_Discipline']
]

BASE_XGB_PARAMS = {
    'enable_categorical': True,
    'n_jobs': -1,
    'n_estimators': N_ESTIMATORS,
    'tree_method': 'hist',
    'random_state': RANDOM_STATE,
    'monotone_constraints': MONOTONE_CONSTRAINTS,
    'interaction_constraints': INTERACTION_CONSTRAINTS,
}
