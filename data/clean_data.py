"""
Cleaning step for the E-Commerce Customer Churn project.
  1. Remove cancelled orders (InvoiceNo starting with 'C' / negative Quantity)
  2. Remove rows with missing CustomerID (can't attribute to a customer)
  3. Remove price outliers (data-entry errors) using an IQR-based cap
  4. Add a LineTotal column and standardize InvoiceDate
"""
import pandas as pd

df = pd.read_csv("retail_transactions_raw.csv", dtype={"CustomerID": "string"})
raw_rows = len(df)

# 1) Remove cancellations
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
df = df[df["Quantity"] > 0]
after_cancel = len(df)

# 2) Remove missing CustomerID
df = df[df["CustomerID"].notna() & (df["CustomerID"].str.strip() != "")]
after_null = len(df)

# 3) Remove price outliers via IQR
q1, q3 = df["UnitPrice"].quantile([0.25, 0.75])
iqr = q3 - q1
upper_bound = q3 + 3 * iqr
df = df[df["UnitPrice"] <= upper_bound]
after_outliers = len(df)

# 4) Derived columns
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%Y %H:%M")
df["LineTotal"] = (df["Quantity"] * df["UnitPrice"]).round(2)
df["CustomerID"] = df["CustomerID"].astype(int)

df = df.sort_values("InvoiceDate").reset_index(drop=True)
df.to_csv("retail_transactions_clean.csv", index=False)

print(f"Raw rows:            {raw_rows}")
print(f"After removing cancellations: {after_cancel}  ({raw_rows - after_cancel} removed)")
print(f"After removing null CustomerID: {after_null}  ({after_cancel - after_null} removed)")
print(f"After removing price outliers:  {after_outliers}  ({after_null - after_outliers} removed)")
print(f"Final clean rows:    {len(df)}")
print(f"Unique customers:    {df['CustomerID'].nunique()}")
print(f"Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")
