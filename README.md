# P01 ⭐ — Retail EDA 📊

## Overview

This project builds a retail exploratory data analysis (EDA) pipeline for analysing sales transactions, store performance, discount impact, and anomalous retail behaviour.

The pipeline loads processed retail transaction data, performs statistical profiling, group-based revenue analysis, correlation analysis, anomaly detection, and generates reports and visualisations.

---

## Table of Contents

1. [Project Brief](#project-brief)
2. [EDA Workflow](#eda-workflow)
3. [Input and Output](#input-and-output)
4. [Project Structure](#project-structure)
5. [Revenue Analysis](#revenue-analysis)
6. [Correlation Analysis](#correlation-analysis)
7. [Anomaly Detection](#anomaly-detection)
8. [Visualisations](#visualisations)
9. [How to Run](#how-to-run)
10. [Tests](#tests)
11. [Git Workflow](#git-workflow)

---

## Project Brief

**Company:** Shop Smart Retail Group  
**Role:** Junior Data Analyst

The retail dataset includes transactional sales records such as:

- Product sales
- Store information
- Discount percentages
- Customer transaction details
- Product category performance
- Payment methods

The analysis focuses on identifying revenue trends, discount effectiveness, and statistically unusual retail transactions.

---

## EDA Workflow

### 1. Load

Load the processed retail dataset from:

```text
data/processed/processed-data.csv
```

The dataset is generated from the ETL pipeline.

---

### 2. Profile

Generate a statistical overview of the retail dataset.

Checks include:

- Row and column counts
- Missing values
- Duplicate records
- Numeric summaries
- Categorical summaries

---

### 3. Group Analysis

Analyse retail revenue performance using groupby operations.

Analysis includes:

- Average revenue by product category
- Average revenue by store
- Revenue ranking
- Underperforming stores relative to category averages

---

### 4. Correlation Analysis

Analyse relationships between numeric retail variables.

The project computes:

- Pearson correlation matrix
- Discount percentage vs total amount relationship
- Strong positive and negative correlations

---

### 5. Anomaly Detection

Detect statistically unusual retail transactions using:

- IQR method
- Z-score method
- Consensus anomaly confirmation

Transactions flagged by both methods are treated as confirmed anomalies.

---

## Input and Output

### Input

```text
data/processed/processed-data.csv
```

### Outputs

```text
reports/analysis_report.txt
reports/anomalies.csv
reports/figures/
```

---

## Project Structure

```text
P01-retail-eda/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── reports/
│   └── figures/
│
├── sql/
│
├── src/
│   ├── data_extractor.py
│   ├── validator.py
│   ├── transformer.py
│   ├── eda_engine.py
│   ├── anomaly_detector.py
│   └── query_runner.py
│
├── tests/
│
├── run.py
├── config.py
├── requirements.txt
└── README.md
```

---

## Revenue Analysis

The project analyses retail revenue performance by:

- Product category
- Store location
- Customer type

Metrics generated include:

- Average revenue per sale
- Total sales revenue
- Revenue ranking
- Store performance comparison

---

## Correlation Analysis

The project evaluates whether discounts affect retail sales performance.

The following variables are analysed:

- `discount_pct`
- `quantity`
- `unit_price`
- `total_amount`

Pearson correlation is used to measure the strength of relationships between variables.

---

## Anomaly Detection

The anomaly detection module identifies transactions that are statistically unusual.

Examples include:

- Extremely high total sales amounts
- Unusual discount percentages
- Abnormal transaction behaviour

Detected anomalies are exported to:

```text
reports/anomalies.csv
```

---

## Visualisations

The notebook generates and saves retail visualisations including:

- Revenue by product category
- Revenue by store
- Retail revenue box plots
- Discount vs total amount scatter plots
- Correlation heatmaps
- Retail anomaly visualisations

Saved charts are stored in:

```text
reports/figures/
```

---

## How to Run

Run the complete retail EDA pipeline:

```bash
python run.py
```

The pipeline performs:

1. SQL extraction
2. Validation
3. Transformation
4. EDA analysis
5. Anomaly detection
6. Report generation

---

## Tests

Run unit tests using:

```bash
pytest tests/
```

Tests cover:

- EDAEngine methods
- Group analysis
- Correlation analysis
- Anomaly detection
- Data quality validation

---

## Git Workflow

```bash
git status
git add .
git commit -m "feat: complete retail EDA pipeline"
git push
```

---

## Success Criteria Achieved

- EDAEngine implemented
- AnomalyDetector implemented
- Revenue ranking analysis completed
- Correlation analysis completed
- Anomalies exported to CSV
- Visualisations generated
- Unit tests completed
- Project pushed to GitHub

---