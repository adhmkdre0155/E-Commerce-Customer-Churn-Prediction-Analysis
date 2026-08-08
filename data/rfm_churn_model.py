"""
RFM feature engineering + churn classification for the E-Commerce Customer Churn project.

Churn definition: a customer is labeled "churned" if their Recency (days since last
purchase, measured from the day after the last date in the dataset) exceeds 90 days.
This mirrors how a retention team would flag at-risk customers today.

Model: trains a Logistic Regression and a Decision Tree on behavioral features
(Frequency, Monetary, AvgOrderValue, Tenure, CancellationRate) to classify churn,
then scores every customer with a churn probability.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

df = pd.read_csv("retail_transactions_clean.csv", parse_dates=["InvoiceDate"])

snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

# ---- RFM aggregation ----
rfm = df.groupby("CustomerID").agg(
    LastPurchase=("InvoiceDate", "max"),
    FirstPurchase=("InvoiceDate", "min"),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("LineTotal", "sum"),
    Country=("Country", "first"),
).reset_index()

rfm["Recency"] = (snapshot_date - rfm["LastPurchase"]).dt.days
rfm["Tenure"] = (rfm["LastPurchase"] - rfm["FirstPurchase"]).dt.days
rfm["AvgOrderValue"] = (rfm["Monetary"] / rfm["Frequency"]).round(2)
rfm["Monetary"] = rfm["Monetary"].round(2)

# Cancellation rate per customer (from raw data, before cancellations were dropped)
raw = pd.read_csv("retail_transactions_raw.csv", dtype={"CustomerID": "string"})
raw = raw[raw["CustomerID"].notna() & (raw["CustomerID"].str.strip() != "")]
raw["CustomerID"] = raw["CustomerID"].astype(int)
raw["IsCancel"] = raw["InvoiceNo"].astype(str).str.startswith("C")
cancel_rate = raw.groupby("CustomerID")["IsCancel"].mean().rename("CancellationRate").round(4)
rfm = rfm.merge(cancel_rate, on="CustomerID", how="left")
rfm["CancellationRate"] = rfm["CancellationRate"].fillna(0)

# ---- Churn label ----
rfm["Churned"] = (rfm["Recency"] > 90).astype(int)

# ---- RFM scoring (quintiles) for segmentation ----
rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

def segment(row):
    if row["R_Score"] >= 4 and row["F_Score"] >= 4:
        return "Champions"
    if row["R_Score"] <= 2 and row["F_Score"] >= 4 and row["M_Score"] >= 4:
        return "At-Risk High Value"
    if row["R_Score"] <= 2 and row["F_Score"] <= 2:
        return "Hibernating"
    if row["R_Score"] >= 4 and row["F_Score"] <= 2:
        return "New / Low Engagement"
    return "Regular"

rfm["Segment"] = rfm.apply(segment, axis=1)

# ---- Model ----
features = ["Frequency", "Monetary", "AvgOrderValue", "Tenure", "CancellationRate"]
X = rfm[features]
y = rfm["Churned"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

logreg = LogisticRegression(max_iter=1000)
logreg.fit(X_train_s, y_train)
logreg_pred = logreg.predict(X_test_s)
logreg_proba = logreg.predict_proba(X_test_s)[:, 1]

tree = DecisionTreeClassifier(max_depth=5, random_state=42, min_samples_leaf=20)
tree.fit(X_train, y_train)
tree_pred = tree.predict(X_test)
tree_proba = tree.predict_proba(X_test)[:, 1]

def report(name, y_true, pred, proba):
    print(f"\n--- {name} ---")
    print(f"Accuracy:  {accuracy_score(y_true, pred):.3f}")
    print(f"Precision: {precision_score(y_true, pred):.3f}")
    print(f"Recall:    {recall_score(y_true, pred):.3f}")
    print(f"F1:        {f1_score(y_true, pred):.3f}")
    print(f"ROC AUC:   {roc_auc_score(y_true, proba):.3f}")

report("Logistic Regression", y_test, logreg_pred, logreg_proba)
report("Decision Tree", y_test, tree_pred, tree_proba)

print("\nDecision Tree feature importances:")
for f, imp in sorted(zip(features, tree.feature_importances_), key=lambda x: -x[1]):
    print(f"  {f}: {imp:.3f}")

# Score every customer with the tree model (best interpretability for the memo)
rfm["ChurnProbability"] = tree.predict_proba(X)[:, 1].round(3)

rfm.to_csv("customer_rfm_churn.csv", index=False)
print(f"\nSaved customer_rfm_churn.csv with {len(rfm)} customers.")

# ---- Headline business insight ----
at_risk_hv = rfm[rfm["Segment"] == "At-Risk High Value"]
print(f"\nAt-Risk High Value segment: {len(at_risk_hv)} customers "
      f"({len(at_risk_hv)/len(rfm)*100:.1f}% of customer base)")
print(f"Revenue at stake (their historical Monetary total): EUR {at_risk_hv['Monetary'].sum():,.0f}")
print(f"Overall churn rate: {rfm['Churned'].mean()*100:.1f}%")
