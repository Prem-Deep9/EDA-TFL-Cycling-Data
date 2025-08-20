# TfL Cycling Data Analysis (2021–2023)

This project provides an end-to-end exploratory data analysis (EDA) and time series forecasting pipeline for Transport for London (TfL) cycle hire data, covering 2021–2023. The goal is to extract actionable insights and prototype machine learning models to support business decisions for short-term bike rental operations.

---

## Project Structure

- **cyclic_data_analysis.ipynb**: Main notebook for EDA, data cleaning, visualization, and time series modeling.
- **file-scrapper-selenium.py**: Script to scrape and download raw CSV data files from the TfL cycling data portal.
- **README.md**: Project documentation (this file).

---

## Data Pipeline

### 1. Data Acquisition

- Use `file-scrapper-selenium.py` to scrape and download all available CSVs from [TfL Cycling Data](https://cycling.data.tfl.gov.uk/).
- The script supports filtering by file number and saves files into the appropriate schema folders.

### 2. Data Preparation

- **Schema Handling**: Data comes in two formats (old and new). The notebook loads, cleans, and normalizes both, then merges them into a unified DataFrame.
- **Cleaning Steps**:
  - Normalize station names (case, whitespace, punctuation).
  - Drop unreliable or redundant columns (e.g., station IDs).
  - Remove duplicate rental records and handle missing values.
  - Convert duration fields to seconds for consistency.

### 3. Exploratory Data Analysis (EDA)

- **Trip Filtering**: Exclude very short trips (≤2 min) and self-loop trips (start = end station) to focus on genuine usage.
- **Outlier Detection**: Identify and analyze long-duration trips and statistical outliers using IQR.
- **Trip Duration Analysis**: Summarize trip duration distribution, quantiles, and typical usage patterns.
- **Temporal Trends**: Analyze ride frequency by hour of day and day of week; visualize with heatmaps.
- **Station Analysis**: Identify top start/end stations, and analyze net flow to find source/sink imbalances.

### 4. Machine Learning & Forecasting

- **Use Cases Outlined**:
  - Demand forecasting (time series)
  - Trip duration prediction (regression)
  - Route/usage pattern clustering (unsupervised)
  - Bike availability prediction (classification/regression)
  - Station rebalancing optimization (operations research)
- **Prototype Model**:
  - Demonstrates daily bike rental forecasting using the `darts` library.
  - Models: Exponential Smoothing and ARIMA.
  - Evaluation: Plots actual vs. predicted rentals, reports MAPE.

---

## How to Run

### 1. Install Dependencies

This project uses `uv` for dependency management. Make sure you have `uv` installed:

```bash
# Install uv if you haven't already
pip install uv
```

Then install the project dependencies:

```bash
uv sync
```

This will create a virtual environment and install all dependencies from `pyproject.toml` and `uv.lock`.

- For scraping: Chrome browser and ChromeDriver must be installed and in PATH.

### 2. Download Data

Run the scraper:

```bash
python file-scrapper-selenium.py
```

Follow prompts to select file ranges and download data.

### 3. Run Analysis

Open `cyclic_data_analysis.ipynb` in Jupyter Notebook or JupyterLab and run all cells.

---

## Key Insights

- **Short trips** (≤2 min) are rare but signal user friction or system issues.
- **Long-duration outliers** (>42 min) represent ~6.5% of trips; extremely long trips (>12 hours) are rare but operationally significant.
- **Peak usage**: Weekday commute hours and weekend afternoons.
- **Station imbalances**: Some stations act as persistent sources or sinks, requiring operational rebalancing.
- **Forecasting**: Simple time series models can predict daily demand, supporting inventory and staffing decisions.