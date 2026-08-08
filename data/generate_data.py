"""
Generates a simulated e-commerce transactions dataset matching the schema of the
public 'Online Retail II' dataset (UCI/Kaggle): InvoiceNo, StockCode, Description,
Quantity, InvoiceDate, UnitPrice, CustomerID, Country.

Note: the real UCI/Kaggle file requires a manual download (no direct API access from
this environment), so this script generates a same-schema, same-scale synthetic
dataset with realistic customer behavior archetypes (loyal, at-risk-high-value,
hibernating, one-time) so churn patterns are genuine and discoverable rather than
scripted. Swap in the real file at data/retail_transactions_raw.csv (same column
names) to re-run the exact same pipeline on real data.
"""
import random
import csv
from datetime import date, timedelta, datetime

random.seed(7)

COUNTRIES = ["United Kingdom"] * 70 + ["Ireland"] * 8 + ["Germany"] * 6 + \
            ["France"] * 6 + ["Netherlands"] * 3 + ["Spain"] * 3 + ["Belgium"] * 2 + ["Portugal"] * 2

PRODUCTS = [
    ("85123A", "WHITE HANGING HEART T-LIGHT HOLDER", 2.55),
    ("71053", "WHITE METAL LANTERN", 3.39),
    ("84406B", "CREAM CUPID HEARTS COAT HANGER", 2.75),
    ("84029G", "KNITTED UNION FLAG HOT WATER BOTTLE", 3.75),
    ("84029E", "RED WOOLLY HOTTIE WHITE HEART", 3.75),
    ("22752", "SET 7 BABUSHKA NESTING BOXES", 7.65),
    ("21730", "GLASS STAR FROSTED T-LIGHT HOLDER", 4.25),
    ("22633", "HAND WARMER UNION JACK", 1.85),
    ("22632", "HAND WARMER RED POLKA DOT", 1.85),
    ("21212", "PACK OF 72 RETROSPOT CAKE CASES", 0.42),
    ("20725", "LUNCH BAG RED RETROSPOT", 1.65),
    ("20727", "LUNCH BAG BLACK SKULL.", 1.65),
    ("22383", "LUNCH BAG SUKI DESIGN", 1.65),
    ("21755", "LOVE BUILDING BLOCK WORD", 5.95),
    ("21754", "HOME BUILDING BLOCK WORD", 5.95),
    ("22960", "JAM MAKING SET WITH JARS", 4.25),
    ("22961", "JAM MAKING SET PRINTED", 1.45),
    ("23203", "JUMBO BAG DOILEY PATTERNS", 2.08),
    ("85099B", "JUMBO BAG RED RETROSPOT", 2.08),
    ("23298", "SPOTTY BUNTING", 4.95),
    ("22086", "PAPER CHAIN KIT 50'S CHRISTMAS", 2.95),
    ("21071", "VINTAGE BILLBOARD DRINK ME MUG", 1.06),
    ("22197", "SMALL POPCORN HOLDER", 0.85),
    ("21931", "JUMBO STORAGE BAG SUKI", 1.95),
    ("22178", "VICTORIAN GLASS HANGING T-LIGHT", 1.25),
    ("21929", "JUMBO BAG PINK VINTAGE PAISLEY", 2.08),
    ("22138", "BAKING SET 9 PIECE RETROSPOT", 4.95),
    ("84879", "ASSORTED COLOUR BIRD ORNAMENT", 1.69),
    ("22423", "REGENCY CAKESTAND 3 TIER", 12.75),
    ("23084", "RABBIT NIGHT LIGHT", 2.08),
]

def rand_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta), seconds=random.randint(0, 86399))

PERIOD_START = date(2010, 12, 1)
PERIOD_END = date(2011, 12, 9)

# Customer archetypes: (share, orders_range, recency_days_range_from_end, avg_qty_mult)
ARCHETYPES = {
    "champion":          {"share": 0.25, "orders": (15, 40), "recency": (0, 30),   "qty_mult": 1.3},
    "at_risk_high_value":{"share": 0.12, "orders": (10, 28), "recency": (95, 260), "qty_mult": 1.4},
    "loyal_low_value":   {"share": 0.20, "orders": (6, 14),  "recency": (0, 45),   "qty_mult": 0.6},
    "hibernating":       {"share": 0.25, "orders": (1, 5),   "recency": (100, 300),"qty_mult": 0.7},
    "one_time":          {"share": 0.18, "orders": (1, 1),   "recency": (0, 373),  "qty_mult": 0.9},
}

N_CUSTOMERS = 4200
customers = []
cust_id = 12346
for name, cfg in ARCHETYPES.items():
    n = int(N_CUSTOMERS * cfg["share"])
    for _ in range(n):
        cust_id += 1
        country = random.choice(COUNTRIES)
        customers.append({"CustomerID": cust_id, "Archetype": name, "Country": country, **cfg})

random.shuffle(customers)

rows = []
invoice_no = 536365

for c in customers:
    n_orders = random.randint(*c["orders"])
    last_purchase_offset = random.randint(*c["recency"])
    last_purchase_date = PERIOD_END - timedelta(days=last_purchase_offset)

    # Spread earlier orders backward from the last purchase date
    order_dates = [last_purchase_date]
    span_days = min(300, (last_purchase_date - PERIOD_START).days)
    for _ in range(n_orders - 1):
        back = random.randint(1, max(span_days, 1))
        d = last_purchase_date - timedelta(days=back)
        if d < PERIOD_START:
            d = PERIOD_START + timedelta(days=random.randint(0, 10))
        order_dates.append(d)

    for od in order_dates:
        invoice_no += 1
        is_cancel = random.random() < 0.025  # ~2.5% of orders are cancellations
        inv_str = ("C" if is_cancel else "") + str(invoice_no)
        n_items = max(1, int(random.gauss(13, 7)))
        ts = datetime.combine(od, datetime.min.time()) + timedelta(
            hours=random.randint(7, 19), minutes=random.randint(0, 59))
        for _ in range(n_items):
            stock, desc, base_price = random.choice(PRODUCTS)
            qty = max(1, int(random.gauss(6, 4) * c["qty_mult"]))
            price = round(base_price * random.uniform(0.9, 1.15), 2)
            if is_cancel:
                qty = -qty
            # Inject rare price outlier (data-entry error) ~0.2% of lines
            if random.random() < 0.002:
                price = round(price * random.uniform(20, 60), 2)
            # ~3% of lines missing CustomerID (guest checkout, needs cleaning)
            cid = "" if random.random() < 0.03 else c["CustomerID"]
            rows.append([inv_str, stock, desc, qty, ts.strftime("%m/%d/%Y %H:%M"),
                         price, cid, c["Country"]])

random.shuffle(rows)

header = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate",
          "UnitPrice", "CustomerID", "Country"]
with open("retail_transactions_raw.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(rows)

print(f"Customers: {len(customers)}")
print(f"Transaction lines: {len(rows)}")
