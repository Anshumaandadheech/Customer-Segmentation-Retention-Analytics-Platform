"""
generate_data.py
================
Generates a realistic online retail dataset simulating ~8000 transactions
from Dec 2010 to Dec 2011, mirroring the well-known UCI Online Retail dataset.

Output: ../data/raw_data.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
np.random.seed(42)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
NUM_CUSTOMERS = 4300
NUM_PRODUCTS = 370
TARGET_ROWS = 25000
DATE_START = pd.Timestamp("2010-12-01")
DATE_END = pd.Timestamp("2011-12-09")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_PATH = OUTPUT_DIR / "raw_data.csv"

# ---------------------------------------------------------------------------
# 1. Product catalog – realistic home-decor / gift / kitchenware items
# ---------------------------------------------------------------------------
ADJECTIVES = [
    "Vintage", "Rustic", "Classic", "Modern", "Retro", "Antique", "Handmade",
    "Decorative", "Elegant", "Charming", "Whimsical", "Colourful", "Natural",
    "Organic", "Polka Dot", "Floral", "Striped", "Paisley", "Jumbo", "Mini",
    "Large", "Small", "Heart", "Star", "Round", "Square", "Wooden", "Metal",
    "Ceramic", "Glass", "Porcelain", "Wicker", "Knitted", "Embroidered",
    "Painted", "Engraved", "Red", "Blue", "Green", "Pink", "White", "Black",
    "Gold", "Silver", "Cream", "Yellow",
]

NOUNS = [
    "Candle Holder", "Photo Frame", "Doormat", "Cushion Cover", "Mug",
    "Tea Light Holder", "Storage Box", "Lunch Bag", "Water Bottle",
    "Coaster Set", "Place Mat", "Napkin Ring", "Cake Stand", "Trinket Box",
    "Wall Sign", "Clock", "Vase", "Bunting", "Garland", "Wind Chime",
    "Bird Feeder", "Plant Pot", "Egg Cup", "Salt & Pepper Set",
    "Butter Dish", "Serving Tray", "Biscuit Tin", "Pencil Case",
    "Notebook", "Greeting Card", "Gift Bag", "Wrapping Paper",
    "Ribbon Reel", "Party Favour", "Paper Chain Kit", "Sticker Sheet",
    "Magnet", "Key Ring", "Bookmark", "Drawer Knob", "Coat Hook",
    "Shelf Unit", "Lantern", "Fairy Lights", "Hanging Decoration",
    "Table Runner", "Apron", "Oven Glove", "Kitchen Timer", "Spice Jar",
    "Oil Burner", "Incense Holder", "Jewellery Box", "Compact Mirror",
    "Hair Clip Set", "Scarf", "Tote Bag", "Shopping Bag", "Lunch Box",
    "Picnic Set", "Placecard Holder", "Bottle Stopper", "Corkscrew",
    "Ice Bucket", "Champagne Flute Set",
]

# Generate unique product descriptions
product_descriptions = set()
while len(product_descriptions) < NUM_PRODUCTS:
    adj = np.random.choice(ADJECTIVES)
    noun = np.random.choice(NOUNS)
    desc = f"{adj} {noun}".upper()
    product_descriptions.add(desc)

product_descriptions = sorted(product_descriptions)

# Generate stock codes (mix of pure numeric and alphanumeric)
stock_codes = []
for i in range(NUM_PRODUCTS):
    if np.random.random() < 0.80:
        # Numeric code: 5 digits
        stock_codes.append(str(10000 + i * 73 + np.random.randint(0, 50)))
    else:
        # Alphanumeric code
        letter = chr(65 + np.random.randint(0, 26))
        stock_codes.append(f"{np.random.randint(1000, 9999)}{letter}")

products_df = pd.DataFrame({
    "StockCode": stock_codes,
    "Description": product_descriptions,
    "BasePrice": np.round(
        np.random.lognormal(mean=1.2, sigma=0.8, size=NUM_PRODUCTS).clip(0.20, 50.0), 2
    ),
})

# ---------------------------------------------------------------------------
# 2. Customer pool
# ---------------------------------------------------------------------------
customer_ids = np.arange(12346, 12346 + NUM_CUSTOMERS)  # IDs like UCI dataset

# Assign each customer a purchase-frequency weight (power-law: few heavy buyers)
purchase_weights = np.random.pareto(a=1.5, size=NUM_CUSTOMERS) + 1
purchase_weights /= purchase_weights.sum()

# ---------------------------------------------------------------------------
# 3. Country distribution (~85% UK)
# ---------------------------------------------------------------------------
COUNTRIES = [
    "United Kingdom", "Germany", "France", "Netherlands", "Australia",
    "Spain", "Belgium", "Switzerland", "Portugal", "Italy",
    "Norway", "Sweden", "Finland", "Denmark", "Austria",
    "Japan", "United Arab Emirates", "USA", "Canada", "Ireland",
    "Poland", "Greece", "Czech Republic", "Israel", "Brazil",
]
COUNTRY_WEIGHTS = np.array([
    0.85, 0.025, 0.02, 0.015, 0.012,
    0.010, 0.008, 0.007, 0.006, 0.006,
    0.005, 0.004, 0.004, 0.003, 0.003,
    0.003, 0.002, 0.002, 0.002, 0.002,
    0.002, 0.001, 0.001, 0.001, 0.001,
])
COUNTRY_WEIGHTS /= COUNTRY_WEIGHTS.sum()  # normalise

# Assign each customer a home country
customer_countries = np.random.choice(COUNTRIES, size=NUM_CUSTOMERS, p=COUNTRY_WEIGHTS)
customer_country_map = dict(zip(customer_ids, customer_countries))

# ---------------------------------------------------------------------------
# 4. Generate invoices (transactions) with seasonal patterns
# ---------------------------------------------------------------------------
NUM_INVOICES = 8000

# Seasonal weighting: months 11 & 12 get ~2× weight
months_in_range = pd.date_range(DATE_START, DATE_END, freq="D")
month_weights = np.array([2.0 if d.month in (11, 12) else 1.0 for d in months_in_range])
month_weights /= month_weights.sum()

invoice_dates_idx = np.random.choice(len(months_in_range), size=NUM_INVOICES, p=month_weights)
invoice_dates = months_in_range[invoice_dates_idx]

# Add random time-of-day (business hours 7am-8pm)
hours = np.random.randint(7, 21, size=NUM_INVOICES)
minutes = np.random.randint(0, 60, size=NUM_INVOICES)
invoice_datetimes = invoice_dates + pd.to_timedelta(hours, unit="h") + pd.to_timedelta(minutes, unit="m")

# Sort chronologically
invoice_datetimes = np.sort(invoice_datetimes)

# Assign invoice numbers (6-digit, ascending)
invoice_start = 536365
invoice_numbers = [str(invoice_start + i) for i in range(NUM_INVOICES)]

# Assign customers to invoices (weighted by purchase frequency)
invoice_customers = np.random.choice(customer_ids, size=NUM_INVOICES, p=purchase_weights)

# ---------------------------------------------------------------------------
# 5. Expand invoices into line items → ~25000 rows
# ---------------------------------------------------------------------------
rows = []
for inv_idx in range(NUM_INVOICES):
    # Each invoice has 1-12 line items (weighted toward 2-5)
    n_items = np.random.choice(
        range(1, 13),
        p=[0.10, 0.18, 0.20, 0.18, 0.12, 0.08, 0.05, 0.03, 0.02, 0.02, 0.01, 0.01],
    )
    # Pick random products
    prod_indices = np.random.choice(NUM_PRODUCTS, size=n_items, replace=False)
    for pi in prod_indices:
        rows.append({
            "InvoiceNo": invoice_numbers[inv_idx],
            "StockCode": products_df.iloc[pi]["StockCode"],
            "Description": products_df.iloc[pi]["Description"],
            "Quantity": None,  # filled below
            "InvoiceDate": invoice_datetimes[inv_idx],
            "UnitPrice": None,  # filled below
            "CustomerID": float(invoice_customers[inv_idx]),
            "Country": customer_country_map[invoice_customers[inv_idx]],
        })

df = pd.DataFrame(rows)
print(f"[INFO] Generated {len(df)} raw line items from {NUM_INVOICES} invoices.")

# Trim or pad to ~25000 rows
if len(df) > TARGET_ROWS:
    df = df.sample(n=TARGET_ROWS, random_state=42).reset_index(drop=True)
elif len(df) < TARGET_ROWS:
    extra = df.sample(n=TARGET_ROWS - len(df), replace=True, random_state=42)
    df = pd.concat([df, extra], ignore_index=True)

# ---------------------------------------------------------------------------
# 6. Quantities – mostly 1-48, some outliers
# ---------------------------------------------------------------------------
base_qty = np.random.lognormal(mean=1.2, sigma=0.7, size=len(df))
df["Quantity"] = np.clip(np.round(base_qty), 1, 48).astype(int)

# Sprinkle in some outliers (top 1%): quantities 50-500
outlier_mask = np.random.random(len(df)) < 0.01
df.loc[outlier_mask, "Quantity"] = np.random.randint(50, 501, size=outlier_mask.sum())

# ---------------------------------------------------------------------------
# 7. Unit prices – add slight noise around base price
# ---------------------------------------------------------------------------
product_price_map = dict(zip(products_df["StockCode"], products_df["BasePrice"]))
df["UnitPrice"] = df["StockCode"].map(product_price_map)
noise = np.random.normal(1.0, 0.05, size=len(df)).clip(0.8, 1.2)
df["UnitPrice"] = np.round(df["UnitPrice"] * noise, 2)
df["UnitPrice"] = df["UnitPrice"].clip(lower=0.20)

# ---------------------------------------------------------------------------
# 8. Inject dirty data
# ---------------------------------------------------------------------------

# 8a. ~5% blank CustomerID
blank_cust_mask = np.random.random(len(df)) < 0.05
df.loc[blank_cust_mask, "CustomerID"] = np.nan
print(f"[DIRTY] Blanked CustomerID in {blank_cust_mask.sum()} rows ({blank_cust_mask.mean():.1%})")

# 8b. ~3% cancelled orders (mark entire invoice)
unique_invoices = df["InvoiceNo"].unique()
n_cancelled = int(len(unique_invoices) * 0.03)
cancelled_invoices = np.random.choice(unique_invoices, size=n_cancelled, replace=False)
cancel_map = {inv: f"C{inv}" for inv in cancelled_invoices}

df["InvoiceNo"] = df["InvoiceNo"].map(lambda x: cancel_map.get(x, x))

# For cancelled invoices, make quantities negative (returns)
cancelled_mask = df["InvoiceNo"].str.startswith("C")
df.loc[cancelled_mask, "Quantity"] = -df.loc[cancelled_mask, "Quantity"].abs()
print(f"[DIRTY] Cancelled {n_cancelled} invoices -> {cancelled_mask.sum()} rows with negative quantities")

# 8c. A few zero unit prices (~0.3%)
zero_price_mask = np.random.random(len(df)) < 0.003
df.loc[zero_price_mask, "UnitPrice"] = 0.00
print(f"[DIRTY] Set zero UnitPrice in {zero_price_mask.sum()} rows")

# 8d. Duplicate rows (~0.5%)
n_dupes = int(len(df) * 0.005)
dupe_rows = df.sample(n=n_dupes, random_state=42)
df = pd.concat([df, dupe_rows], ignore_index=True)
print(f"[DIRTY] Added {n_dupes} duplicate rows")

# ---------------------------------------------------------------------------
# 9. Final shuffle & sort by date
# ---------------------------------------------------------------------------
df = df.sort_values("InvoiceDate").reset_index(drop=True)

# Format CustomerID as integer where not NaN (for clean display)
# Keep as float to preserve NaN
df["CustomerID"] = df["CustomerID"].astype("Int64")  # nullable integer

# Format InvoiceDate nicely
df["InvoiceDate"] = df["InvoiceDate"].dt.strftime("%Y-%m-%d %H:%M")

# ---------------------------------------------------------------------------
# 10. Save to CSV
# ---------------------------------------------------------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)
print(f"\n[OUTPUT] Saved {len(df)} rows to {OUTPUT_PATH}")

# ---------------------------------------------------------------------------
# 11. Summary statistics
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("DATASET SUMMARY STATISTICS")
print("=" * 60)
print(f"Total rows:              {len(df):,}")
print(f"Unique invoices:         {df['InvoiceNo'].nunique():,}")
print(f"Unique customers:        {df['CustomerID'].dropna().nunique():,}")
print(f"Unique products:         {df['StockCode'].nunique():,}")
print(f"Unique countries:        {df['Country'].nunique():,}")
print(f"Date range:              {df['InvoiceDate'].min()} -> {df['InvoiceDate'].max()}")
print(f"")
print(f"--- Data Quality Issues ---")
print(f"Missing CustomerID:      {df['CustomerID'].isna().sum():,} ({df['CustomerID'].isna().mean():.1%})")
print(f"Cancelled orders (C*):   {df['InvoiceNo'].str.startswith('C').sum():,} ({df['InvoiceNo'].str.startswith('C').mean():.1%})")
print(f"Negative quantities:     {(df['Quantity'] < 0).sum():,}")
print(f"Zero unit prices:        {(df['UnitPrice'] == 0).sum():,}")
n_exact_dupes = df.duplicated().sum()
print(f"Exact duplicate rows:    {n_exact_dupes:,}")
print(f"")
print(f"--- Quantity Stats ---")
print(df["Quantity"].describe().to_string())
print(f"")
print(f"--- UnitPrice Stats ---")
print(df["UnitPrice"].describe().to_string())
print(f"")
print(f"--- Top 5 Countries ---")
print(df["Country"].value_counts().head(5).to_string())
print("=" * 60)
