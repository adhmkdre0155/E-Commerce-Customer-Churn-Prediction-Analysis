"""
Loads retail_transactions_clean.csv and customer_rfm_churn.csv into a local
SQLite database (retail_churn.db) so sql/queries.sql can be run.
Run this after generate_data.py and clean_data.py (or after rfm_churn_model.py
for the customer_rfm table).
"""
import sqlite3
import pandas as pd

tx = pd.read_csv("../data/retail_transactions_clean.csv", parse_dates=["InvoiceDate"])
rfm = pd.read_csv("../data/customer_rfm_churn.csv")

con = sqlite3.connect("retail_churn.db")
tx.to_sql("transactions", con, if_exists="replace", index=False)
rfm.to_sql("customer_rfm", con, if_exists="replace", index=False)
con.close()

print(f"Loaded {len(tx)} transactions and {len(rfm)} customers into retail_churn.db")
