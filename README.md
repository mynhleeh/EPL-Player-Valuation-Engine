# EPL Player Analytics & Market Valuation System (2024-2025)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask-red.svg)](https://flask.palletsprojects.com/)
[![ML](https://img.shields.io/badge/ML-XGBoost-orange.svg)](https://xgboost.readthedocs.io/)
[![Database](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)

A comprehensive data science project designed to scrape, analyze, and predict the market value of English Premier League players for the 2024-2025 season. This system integrates automated web crawling, RESTful API development, advanced statistical profiling, and machine learning.

---

## 🚀 Features

- **Automated Data Pipeline**: Scrapes FBref for match statistics and FootballTransfers for market values using `SeleniumBase` (Undetected Chrome mode).
- **RESTful API**: A robust Flask-based backend providing endpoints for player and squad lookups.
- **CLI Tool**: A command-line interface to query player stats and export results to formatted CSV/Table files.
- **Squad Analytics**: Multivariate weighted ranking models to identify the best-performing teams.
- **Player Profiling**: K-Means clustering with PCA visualization to categorize players by playing style.
- **Market Valuation**: An XGBoost regression model optimized with Optuna to detect undervalued "hidden gems" in the transfer market.

---

## 📂 Project Structure

```text
.
├── data/                   # Database (SQLite), CSV outputs, and charts
├── docs/                   # Technical report (LaTeX) and documentation
├── source_code/
│   ├── part1/              # Data crawling and fuzzy matching scripts
│   ├── part2/              # Flask API and CLI lookup tool
│   └── part3/              # Analytics, Clustering, and Machine Learning
│       └── core/           # Shared modules (config, training, charts, etc.)
├── requirements.txt        # Full project dependencies
└── README.md               # You are here
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- Google Chrome (latest version)
- ChromeDriver (handled automatically by SeleniumBase)

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/mynhleeh/Python-Programming-Project.git
   cd Python-Programming-Project
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # OR
   .venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📖 Usage Guide

### 1. Data Collection
Build the database by scraping fresh data:
```bash
python source_code/part1/crawl_data.py
python source_code/part1/crawl_transfer.py
```

### 2. Search & Lookup
**Start the API Server**:
```bash
python source_code/part2/app.py
```
**Use the CLI Client** (in a separate terminal):
```bash
python source_code/part2/lookup.py --name "Salah" --club "Liverpool"
```

### 3. Analytics & Machine Learning
Generate squad rankings, player clusters, and the valuation model:
```bash
python source_code/part3/squad_analytics.py
python source_code/part3/clusters.py
python source_code/part3/evaluation.py
```

---

## 📊 Methodology Highlights

- **Anti-Bot Navigation**: Uses `SeleniumBase` with UC mode to bypass Cloudflare protection.
- **Fuzzy Matching**: Implements `thefuzz` (Levenshtein distance) to link player names across disparate datasets.
- **Dimensionality Reduction**: Employs PCA to visualize 4D player clusters in 2D/3D space.
- **Hyperparameter Tuning**: Utilizes Bayesian optimization via `Optuna` for the XGBoost regressor.
- **Financial Status**: Classifies players as *Undervalued* or *Overvalued* based on residual error analysis ($\text{Actual} - \text{Predicted}$).

---

## 📝 License
This project is for educational purposes as part of the Python Programming course at PTIT.

**Author**: [Lê Anh Minh](https://github.com/mynhleeh) & Team