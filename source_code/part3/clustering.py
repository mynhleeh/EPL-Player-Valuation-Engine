from sklearn.preprocessing import RobustScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

base_dir = Path(__file__).resolve().parent.parent.parent
path = base_dir / "data"


def fetch_data():
    with sqlite3.connect(str(path / "database.db")) as conn:
        df = pd.read_sql("SELECT * FROM statistic", conn)

        # remove GK
        df = df[df['Pos'] != 'GK']

        # Add more features
        df['Agg_per90'] = (df['CrdY_perf'] + 2 * df['CrdR_perf']) / df['90s']
        df['PK_per90'] = df['PK_perf'] / df['90s']

        # Main features
        df = df.loc[:, ['Gls_per90', 'Ast_per90', 'Agg_per90', 'PK_per90']]
        return df


def create_charts(elbow: list, silhouettes: list, max_k=10):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    ax1.plot(range(2, max_k + 1), elbow, marker='o', color='b')
    ax1.set_title('Elbow chart')

    ax2.plot(range(2, max_k + 1), silhouettes, marker='s', color='r')
    ax2.set_title('Silhouettes chart')

    plt.tight_layout()
    plt.savefig(str(path / "Elbow and Silhouettes chart"), dpi=900, bbox_inches='tight', facecolor='white')
    # plt.show()


def tryKclutters(data: pd.DataFrame, max_k=10):
    elbow, silhouettes = [], []

    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, init='k-means++', n_init=10).fit(data)
        kmeans._estimator_type = "clusterer"

        elbow.append(kmeans.inertia_)
        silhouettes.append(silhouette_score(data, kmeans.labels_))

    create_charts(elbow, silhouettes, max_k)


def reshape(df: pd.DataFrame, dimen: int):
    new_arr = PCA(n_components=dimen).fit_transform(df)

    cols = ['X', 'Y']
    if dimen == 3: cols.append('Z')

    return pd.DataFrame(data=new_arr, columns=cols)


def scatter_chart(df: pd.DataFrame, kmeans: KMeans, dimen: int):
    df = reshape(df, dimen)
    fig = plt.figure(figsize=(10, 8))

    if dimen == 2:
        ax = plt.gca()
        scatter = plt.scatter(x=df['X'], y=df['Y'], c=kmeans.labels_, cmap='viridis')
    elif dimen == 3:
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(xs=df['X'], ys=df['Y'], zs=df['Z'], c=kmeans.labels_,
                         cmap='viridis', s=50, alpha=0.75, depthshade=True)
    else: return

    plt.colorbar(scatter, ax=ax, label='Cluster')
    plt.title(f"K-Means Clustering {dimen}D Visualization")

    plt.savefig(str(path / f"K-Means {dimen}D.png"), dpi=900, bbox_inches='tight', facecolor='white')
    # plt.show()


if __name__ == '__main__':
    raw_data = fetch_data()
    scaled_data = pd.DataFrame(RobustScaler().fit_transform(raw_data))
    tryKclutters(scaled_data)

    bestK = int(input('Enter best K for K-Means Algorithm: '))
    kmeans = KMeans(n_clusters=bestK, init='k-means++', n_init=10).fit(scaled_data)

    scatter_chart(scaled_data, kmeans, 2)
    scatter_chart(scaled_data, kmeans, 3)