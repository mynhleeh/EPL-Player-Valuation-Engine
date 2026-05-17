# EPL Player Valuation & Analytics Engine

> [!NOTE]  
> **Branch Context:**  
> This development branch was created to ensure the project's overall progress and completion quality. Since this is a development branch, the following documentation only focuses on a brief summary of the project structure and basic execution instructions.


## 📊 Project Overview

This system provides a comprehensive, end-to-end workflow—from data collection (pipeline) and querying services (Flask API & CLI) to deep statistical analysis and machine learning applications on English Premier League (EPL) player statistics for the 2024-2025 season.

The project is structured into three main parts corresponding to the subdirectories under `source_code/`:

```text
source_code/
├── pipeline/       # PART I: Data Pipeline (Web Crawling & Database)
├── client/         # PART II: Query Services (Flask API Server & CLI Client)
└── analytics/      # PART III: Analytics & Machine Learning (PCA, K-Means & Valuation)
```


## 📂 Detailed Structure & Execution Guide

### 🛠️ Part I: Data Pipeline (`source_code/pipeline/`)
Responsible for raw data collection and centralized storage in an SQLite database.
*   **`stats.py`**: Crawls performance statistics for all EPL 2024-2025 players with > 90 minutes of playtime from [FBref](https://fbref.com/en/).
*   **`prices.py`**: Crawls transfer values for each player from [FootballTransfers](https://www.footballtransfers.com).

*Execution:*
```bash
# Collect player performance statistics and store in SQLite
python source_code/pipeline/stats.py

# Collect player transfer values
python source_code/pipeline/prices.py
```

---

### 🌐 Part II: Services & Clients (`source_code/client/`)
Provides a RESTful API to query player data along with a command-line interface (CLI) tool.
*   **`server.py`**: Launches a RESTful API server using **Flask RESTful** to support queries by player name or club name.
*   **`lookup.py`**: A CLI client program to quickly query the database via the API server, displaying results as a formatted table in the console and exporting them to a CSV file.

*Execution:*
1. **Start the Flask API Server:**
   ```bash
   python source_code/client/server.py
   ```
2. **Use the CLI Client to query (while the server is running):**
   ```bash
   # Query by player name
   python source_code/client/lookup.py --name "Erling Haaland"

   # Query by club name
   python source_code/client/lookup.py --club "Arsenal"
   ```

---

### 🧠 Part III: Analytics & Machine Learning (`source_code/analytics/`)
Performs advanced data analysis, player valuation modeling, and machine learning clustering.
*   **`squad_analytics.py`**: Calculates team statistics (median, mean, standard deviation) for each squad and exports the results to a CSV report.
*   **`evaluation.py`**: Defines the methodology/model to automatically estimate player value based on their actual performance metrics.
*   **`clusters.py`**: Classifies players using **K-Means** clustering (with Elbow and Silhouette methods to determine the optimal number of clusters $K$) and visualizes clustering results using **PCA** dimensional reduction in 2D and 3D.
*   **`core/`**: Helper modules for feature engineering (`features.py`), training pipelines (`training.py`), chart generation (`charts.py`), and data loading (`loader.py`).

*Execution:*
```bash
# Analyze squad statistics
python source_code/analytics/squad_analytics.py

# Run K-Means clustering, optimize clusters, and generate PCA plots
python source_code/analytics/clusters.py
```


## ⚙️ Installation & Requirements

The project primarily relies on standard Python libraries for Data Science and Web APIs. Please ensure you have the following packages installed before running the system:
*   `requests`
*   `beautifulsoup4`
*   `flask`
*   `flask-restful`
*   `pandas`
*   `numpy`
*   `scikit-learn`
*   `matplotlib`
*   `seaborn`

*Quick install:*
```bash
pip install requests beautifulsoup4 flask flask-restful pandas numpy scikit-learn matplotlib seaborn
```