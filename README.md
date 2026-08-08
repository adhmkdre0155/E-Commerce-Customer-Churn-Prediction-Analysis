# E-Commerce Customer Churn Prediction & Analysis

**Data Analyst portfolio project — Adham AlHers**
[Live interactive dashboard](./dashboard/index.html) · [LinkedIn](#) · [Portfolio home](#)

## Problem statement
An online retailer wants to know which customers are at risk of not returning, so retention marketing can target them before they churn — rather than relying on blanket, margin-eroding discounts.

## Business context
Customer acquisition cost typically runs 5–7x retention cost — highly relevant to Irish e-commerce operators competing on repeat purchase rate rather than one-off acquisition.

## Dataset
A simulated dataset matching the schema of the public **Online Retail II** dataset (UCI/Kaggle): `InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country`. The real file requires a manual download from UCI/Kaggle (no direct API access), so `data/generate_data.py` generates a same-schema, same-scale dataset (**646K raw transaction lines, 4,200 customers**) with realistic behavioral archetypes — Champions, At-Risk High Value, Loyal Low Value, Hibernating, One-Time Buyers — so churn patterns are genuine and discoverable, not scripted. Swap in the real UCI file (same column names) to re-run the identical pipeline on real data.

## Tools
Python (pandas, scikit-learn) for cleaning, RFM engineering, and churn modeling · SQL (SQLite) for segment/country analysis · Excel (openpyxl, formula-driven) for the KPI dashboard · Chart.js for the interactive web dashboard.

## Repository structure
```
├── data/
│   ├── generate_data.py                     # Generates the raw simulated dataset
│   ├── clean_data.py                        # Removes cancellations, nulls, price outliers
│   ├── rfm_churn_model.py                   # RFM engineering + churn classification
│   ├── retail_transactions_raw_SAMPLE.csv   # 2,000-row sample (full file is 646K rows / ~52MB, regenerate locally — see below)
│   ├── retail_transactions_clean_SAMPLE.csv # 2,000-row sample of the cleaned data
│   └── customer_rfm_churn.csv               # Full output: one row per customer (RFM + segment + churn score)
├── sql/
│   ├── queries.sql                 # Churn rate by country/segment, RFM matrix, funnel
│   └── load_db.py                  # Loads the full local CSVs into SQLite to run queries.sql
├── excel/
│   └── Ecommerce_Churn_Dashboard.xlsx
├── dashboard/
│   └── index.html                  # Self-contained interactive web dashboard
└── docs/
    ├── insights_memo.docx
    └── insights_memo.pdf
```

**Note on the sample CSVs:** the full raw/clean transaction files (646K and 590K rows) are ~52MB each — too large to be a good GitHub citizen, so this repo ships a 2,000-row sample of each for quick inspection instead. To work with the full dataset locally: run `python data/generate_data.py` then `python data/clean_data.py` (takes a few seconds), which regenerates the full CSVs exactly as used to produce every number in this README, the dashboard, and the memo. `customer_rfm_churn.csv` (the actual per-customer analysis output, 4,176 rows) is small enough to ship in full and is included as-is.

## Step-by-step approach
1. **Clean** — `data/clean_data.py` removes cancelled orders (negative quantity / 'C'-prefixed invoices), rows with missing CustomerID, and price outliers via an IQR cap. 646,146 → 590,693 clean transaction lines.
2. **Engineer RFM features** — `data/rfm_churn_model.py` aggregates to one row per customer: Recency, Frequency, Monetary, Tenure, AvgOrderValue, CancellationRate.
3. **Define & model churn** — churn = no purchase in 90+ days. Trained a Logistic Regression (baseline) and a Decision Tree (final model, max depth 5) on behavioral features to classify churn and score every customer with a churn probability.
4. **Segment with RFM scoring** — quintile-scored Recency/Frequency/Monetary into named segments (Champions, At-Risk High Value, Regular, Hibernating, New/Low Engagement).
5. **Query in SQL** — `sql/queries.sql` covers churn rate by country and segment, the RFM matrix, and the recency-bucketed retention funnel.
6. **Visualize** — formula-driven Excel dashboard + a self-contained interactive HTML dashboard (funnel, RFM heatmap, segment revenue, country churn rate).

## Model performance
| Model | Accuracy | Precision | Recall | ROC AUC |
|---|---|---|---|---|
| Logistic Regression | 0.892 | 0.891 | 0.896 | 0.920 |
| Decision Tree (max depth 5) | 0.940 | 0.902 | 0.989 | 0.975 |

**Honest caveat:** this performance is unusually strong because the simulated customer archetypes create clean behavioral separation, which the model exploits easily (Tenure alone accounts for ~83% of the Decision Tree's feature importance). On real, noisier transaction data I'd expect a meaningfully lower ROC AUC — typically 0.75–0.85 for production churn models. I'm flagging this directly rather than presenting the metric uncritically, since recognizing when a model is "too good" is itself part of the analysis.

## Key insight
**297 customers (7.1% of the customer base)** sit in the **At-Risk High Value** segment — historically frequent, high-spending buyers who haven't purchased in 90+ days — representing **€1,737,543** in historical revenue now at risk of being lost permanently.

A secondary finding: **Ireland has the second-highest churn rate (57.6%, n=316)** of any sizeable market in the dataset, just behind Portugal — a market-specific angle directly relevant to an Irish retention team.

## Recommendation
Launch a targeted win-back campaign (personalized offer + re-engagement sequence) for the At-Risk High Value segment specifically, rather than a blanket site-wide discount — this segment has already proven willingness to spend, so the barrier is re-engagement, not price sensitivity.

## Business impact
Replaces blanket, margin-eroding discount campaigns with a targeted list a retention team can act on directly, and surfaces a country-level pattern (Ireland) worth a dedicated follow-up.

## CV / LinkedIn bullet
> Built a churn-prediction model (Python/scikit-learn) on 590K+ e-commerce transactions across 4,176 customers; flagged a high-value at-risk segment worth an estimated €1.7M in historical revenue, and identified Ireland as a market-specific retention priority.

---
*Dataset is simulated for portfolio purposes, matching the schema and scale of the public Online Retail II dataset. All cleaning, modeling, and SQL logic is fully reproducible.*
