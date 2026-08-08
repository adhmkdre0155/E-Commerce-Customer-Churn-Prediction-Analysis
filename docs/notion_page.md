# 📊 E-Commerce Customer Churn Prediction & Analysis

**Type:** Data Analyst project · **Tools:** Python (Pandas, scikit-learn), SQL, Excel, interactive dashboard · **Status:** Complete

[🔗 Live interactive dashboard](#) · [🔗 GitHub repository](#) · [📄 Insights memo (PDF)](#)

---

### The problem
An online retailer wants to know which customers are at risk of not returning, so retention marketing can target them before they churn — instead of relying on blanket, margin-eroding discounts.

### Business context
Customer acquisition cost runs 5–7x retention cost — directly relevant to Irish e-commerce operators competing on repeat purchase rate.

### Dataset
Simulated dataset matching the schema of the public **Online Retail II** dataset (UCI/Kaggle) — 646K raw transaction lines, 4,200 customers, built with realistic behavioral archetypes so churn patterns are genuine and discoverable.

### What I did
1. **Cleaned** the data — removed cancelled orders, missing CustomerIDs, and price outliers (646K → 590K clean lines).
2. **Engineered RFM features** (Recency, Frequency, Monetary + Tenure, AvgOrderValue) per customer in Python/Pandas.
3. **Defined churn** (no purchase in 90+ days) and trained a Logistic Regression and Decision Tree in scikit-learn to classify at-risk customers.
4. **Segmented customers** using RFM scoring into Champions, At-Risk High Value, Regular, Hibernating, and New/Low Engagement.
5. **Queried in SQL** — churn rate by country and segment, RFM matrix, retention funnel.
6. **Visualized** in a formula-driven Excel dashboard and a self-contained interactive web dashboard.

### 🔑 Key insight
> **297 customers (7.1% of the customer base)** sit in the **At-Risk High Value** segment — historically frequent, high-spending buyers who haven't purchased in 90+ days — representing **€1,737,543** in historical revenue now at risk. A secondary finding: **Ireland has the second-highest churn rate (57.6%)** of any sizeable market in the dataset.

### Recommendation
Launch a targeted win-back campaign for the At-Risk High Value segment specifically — this group has already proven willingness to spend, so the barrier is re-engagement, not price.

### A note on model performance
The Decision Tree scored a 0.975 ROC AUC — unusually strong, and worth being upfront about rather than presenting uncritically: the simulated archetypes create cleaner separation than real customer data typically shows. On real transaction data, 0.75–0.85 ROC AUC would be a more realistic expectation. Flagging this directly in the write-up and dashboard.

### Business impact
Replaces blanket, margin-eroding discounting with a targeted, actionable list for the retention team, plus a market-specific lead (Ireland) worth a dedicated follow-up.

---

**CV / LinkedIn bullet:**
*Built a churn-prediction model (Python/scikit-learn) on 590K+ e-commerce transactions across 4,176 customers; flagged a high-value at-risk segment worth an estimated €1.7M in historical revenue, and identified Ireland as a market-specific retention priority.*

**Skills demonstrated:** Data cleaning · Feature engineering (RFM) · Classification modeling (scikit-learn) · SQL · Data visualization · Critical evaluation of model results · Business recommendation writing
