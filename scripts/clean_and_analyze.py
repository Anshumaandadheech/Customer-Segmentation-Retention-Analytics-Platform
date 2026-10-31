"""
E-commerce Data Cleaning & Analysis Pipeline
=============================================
This script:
1. Loads the raw dataset
2. Cleans the data (removes blanks, cancellations, invalid values)
3. Creates derived columns (Sales, date fields)
4. Computes core business metrics
5. Performs RFM customer segmentation
6. Builds cohort retention analysis
7. Exports all results as JSON for the dashboard
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime

# Configure utf-8 stdout for Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================
BASE_DIR = r"C:\Users\Anshumaan\.gemini\antigravity\scratch\ecommerce-customer-analysis"
RAW_DATA = os.path.join(BASE_DIR, "data", "raw_data.csv")
CLEAN_DATA = os.path.join(BASE_DIR, "data", "cleaned_data.csv")
DASHBOARD_DATA = os.path.join(BASE_DIR, "dashboard", "dashboard_data.json")

print("=" * 60)
print("E-COMMERCE DATA CLEANING & ANALYSIS PIPELINE")
print("=" * 60)

# ============================================================
# STEP 1: LOAD RAW DATA
# ============================================================
print("\n📂 Loading raw data...")
df_raw = pd.read_csv(RAW_DATA, encoding='utf-8')
print(f"   Raw dataset: {len(df_raw):,} rows × {len(df_raw.columns)} columns")
print(f"   Columns: {list(df_raw.columns)}")
print(f"   Missing values:\n{df_raw.isnull().sum().to_string()}")

# ============================================================
# STEP 2: CLEAN THE DATA
# ============================================================
print("\n🧹 Cleaning data...")

df = df_raw.copy()
initial_rows = len(df)

# 2a. Remove rows where CustomerID is blank
null_customers = df['CustomerID'].isnull().sum()
df = df.dropna(subset=['CustomerID'])
print(f"   Removed {null_customers:,} rows with blank CustomerID")

# 2b. Remove cancelled orders (InvoiceNo starting with 'C')
df['InvoiceNo'] = df['InvoiceNo'].astype(str)
cancelled = df['InvoiceNo'].str.startswith('C').sum()
df = df[~df['InvoiceNo'].str.startswith('C')]
print(f"   Removed {cancelled:,} cancelled order rows")

# 2c. Remove zero or negative quantities and prices
bad_qty = (df['Quantity'] <= 0).sum()
df = df[df['Quantity'] > 0]
print(f"   Removed {bad_qty:,} rows with zero/negative quantity")

bad_price = (df['UnitPrice'] <= 0).sum()
df = df[df['UnitPrice'] > 0]
print(f"   Removed {bad_price:,} rows with zero/negative price")

# 2d. Remove duplicates
dupes = df.duplicated().sum()
df = df.drop_duplicates()
print(f"   Removed {dupes:,} duplicate rows")

# 2e. Check for missing product descriptions
missing_desc = df['Description'].isnull().sum()
if missing_desc > 0:
    df['Description'] = df['Description'].fillna('Unknown Product')
    print(f"   Filled {missing_desc:,} missing product descriptions")

final_rows = len(df)
print(f"\n   ✅ Cleaned: {initial_rows:,} → {final_rows:,} rows ({initial_rows - final_rows:,} removed, {(initial_rows - final_rows)/initial_rows*100:.1f}%)")

# ============================================================
# STEP 3: CREATE DERIVED COLUMNS
# ============================================================
print("\n📊 Creating derived columns...")

# Sales column
df['Sales'] = df['Quantity'] * df['UnitPrice']
df['Sales'] = df['Sales'].round(2)

# Parse dates
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Date fields
df['OrderMonth'] = df['InvoiceDate'].dt.month
df['OrderYear'] = df['InvoiceDate'].dt.year
df['YearMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
df['Hour'] = df['InvoiceDate'].dt.hour

# Ensure CustomerID is string
df['CustomerID'] = df['CustomerID'].astype(int).astype(str)

print(f"   Created: Sales, OrderMonth, OrderYear, YearMonth, DayOfWeek, Hour")

# Save cleaned data
df.to_csv(CLEAN_DATA, index=False)
print(f"   💾 Saved cleaned data to: {CLEAN_DATA}")

# ============================================================
# STEP 4: CORE BUSINESS METRICS
# ============================================================
print("\n" + "=" * 60)
print("CORE BUSINESS METRICS")
print("=" * 60)

total_revenue = df['Sales'].sum()
total_orders = df['InvoiceNo'].nunique()
total_customers = df['CustomerID'].nunique()
total_products = df['StockCode'].nunique()
avg_order_value = total_revenue / total_orders
avg_items_per_order = df.groupby('InvoiceNo')['Quantity'].sum().mean()
date_range_start = df['InvoiceDate'].min().strftime('%Y-%m-%d')
date_range_end = df['InvoiceDate'].max().strftime('%Y-%m-%d')

print(f"   Total Revenue:        ${total_revenue:,.2f}")
print(f"   Total Orders:         {total_orders:,}")
print(f"   Total Customers:      {total_customers:,}")
print(f"   Total Products:       {total_products:,}")
print(f"   Avg Order Value:      ${avg_order_value:,.2f}")
print(f"   Avg Items/Order:      {avg_items_per_order:,.1f}")
print(f"   Date Range:           {date_range_start} to {date_range_end}")

# Revenue by month
print("\n📈 Revenue by Month:")
rev_by_month = df.groupby('YearMonth')['Sales'].sum().reset_index()
rev_by_month.columns = ['YearMonth', 'Revenue']
rev_by_month = rev_by_month.sort_values('YearMonth')
for _, row in rev_by_month.iterrows():
    print(f"   {row['YearMonth']}: ${row['Revenue']:,.2f}")

# Revenue by country
print("\n🌍 Revenue by Country (Top 10):")
rev_by_country = df.groupby('Country')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
rev_by_country.columns = ['Country', 'Revenue']
for _, row in rev_by_country.iterrows():
    print(f"   {row['Country']}: ${row['Revenue']:,.2f}")

# Top 10 products by revenue
print("\n🏆 Top 10 Products by Revenue:")
top_products_rev = df.groupby(['StockCode', 'Description'])['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
top_products_rev.columns = ['StockCode', 'Description', 'Revenue']
for i, row in top_products_rev.iterrows():
    print(f"   {row['Description'][:40]:40s} ${row['Revenue']:>10,.2f}")

# Top 10 products by quantity
print("\n📦 Top 10 Products by Quantity Sold:")
top_products_qty = df.groupby(['StockCode', 'Description'])['Quantity'].sum().sort_values(ascending=False).head(10).reset_index()
top_products_qty.columns = ['StockCode', 'Description', 'Quantity']
for i, row in top_products_qty.iterrows():
    print(f"   {row['Description'][:40]:40s} {row['Quantity']:>8,}")

# Top customers by lifetime value
print("\n💎 Top 10 Customers by Lifetime Value:")
clv = df.groupby('CustomerID')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
clv.columns = ['CustomerID', 'LifetimeValue']
for _, row in clv.iterrows():
    print(f"   Customer {row['CustomerID']}: ${row['LifetimeValue']:,.2f}")

# ============================================================
# STEP 5: RFM CUSTOMER SEGMENTATION
# ============================================================
print("\n" + "=" * 60)
print("RFM CUSTOMER SEGMENTATION")
print("=" * 60)

# Reference date = max date in dataset + 1 day
reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
print(f"   Reference date: {reference_date.strftime('%Y-%m-%d')}")

# Calculate RFM values per customer
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
    'InvoiceNo': 'nunique',                                      # Frequency
    'Sales': 'sum'                                                # Monetary
}).reset_index()

rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
rfm['Monetary'] = rfm['Monetary'].round(2)

print(f"\n   RFM Statistics:")
print(f"   {'Metric':<12} {'Mean':>10} {'Median':>10} {'Min':>10} {'Max':>10}")
print(f"   {'-'*52}")
for col in ['Recency', 'Frequency', 'Monetary']:
    print(f"   {col:<12} {rfm[col].mean():>10.1f} {rfm[col].median():>10.1f} {rfm[col].min():>10.1f} {rfm[col].max():>10.1f}")

# Assign scores 1-5 using quantiles
# For Recency, lower is better so we reverse (5 = most recent)
rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop').astype(int)
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)

rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

# Segment assignment
def assign_segment(row):
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'
    elif r >= 4 and f >= 4 and m < 4:
        return 'Loyal Customers'
    elif f >= 3 and m >= 3:
        if r >= 3:
            return 'Loyal Customers'
        else:
            return 'At Risk'
    elif r >= 4 and f >= 1 and f <= 2:
        return 'New Customers'
    elif r >= 3 and f >= 2:
        return 'Potential Loyalists'
    elif r <= 2 and f >= 2:
        return 'At Risk'
    elif r <= 2 and f <= 1:
        return 'Lost Customers'
    elif r >= 3 and f <= 1:
        return 'Promising'
    else:
        return 'Need Attention'

rfm['Segment'] = rfm.apply(assign_segment, axis=1)

print("\n   📊 Segment Distribution:")
segment_dist = rfm['Segment'].value_counts().reset_index()
segment_dist.columns = ['Segment', 'Count']
segment_dist['Percentage'] = (segment_dist['Count'] / len(rfm) * 100).round(1)
segment_dist['Avg_Revenue'] = segment_dist['Segment'].apply(
    lambda s: rfm[rfm['Segment'] == s]['Monetary'].mean()
).round(2)

for _, row in segment_dist.iterrows():
    print(f"   {row['Segment']:<22} {row['Count']:>5} customers ({row['Percentage']:>5.1f}%)  Avg Revenue: ${row['Avg_Revenue']:>10,.2f}")

# Save RFM data
rfm_output = os.path.join(BASE_DIR, "data", "rfm_segmentation.csv")
rfm.to_csv(rfm_output, index=False)
print(f"\n   💾 Saved RFM data to: {rfm_output}")

# ============================================================
# STEP 6: COHORT RETENTION ANALYSIS
# ============================================================
print("\n" + "=" * 60)
print("COHORT RETENTION ANALYSIS")
print("=" * 60)

# Find each customer's first purchase month (cohort)
df['OrderPeriod'] = df['InvoiceDate'].dt.to_period('M')
cohort_data = df.groupby('CustomerID')['OrderPeriod'].min().reset_index()
cohort_data.columns = ['CustomerID', 'CohortPeriod']

# Merge back
df_cohort = df.merge(cohort_data, on='CustomerID')

# Calculate cohort index (months since first purchase)
df_cohort['CohortIndex'] = (
    (df_cohort['OrderPeriod'].dt.year - df_cohort['CohortPeriod'].dt.year) * 12 +
    (df_cohort['OrderPeriod'].dt.month - df_cohort['CohortPeriod'].dt.month)
)

# Count unique customers per cohort and cohort index
cohort_counts = df_cohort.groupby(['CohortPeriod', 'CohortIndex'])['CustomerID'].nunique().reset_index()
cohort_counts.columns = ['CohortPeriod', 'CohortIndex', 'CustomerCount']

# Pivot to create cohort table
cohort_pivot = cohort_counts.pivot(index='CohortPeriod', columns='CohortIndex', values='CustomerCount')
cohort_pivot.index = cohort_pivot.index.astype(str)

# Get cohort sizes (Month 0)
cohort_sizes = cohort_pivot[0]

# Calculate retention rates
retention = cohort_pivot.divide(cohort_sizes, axis=0)
retention = (retention * 100).round(1)

print("\n   Cohort Retention Rates (%):")
print(retention.to_string())

# Save cohort data
cohort_output = os.path.join(BASE_DIR, "data", "cohort_retention.csv")
retention.to_csv(cohort_output)
print(f"\n   💾 Saved cohort retention to: {cohort_output}")

# ============================================================
# STEP 7: PREPARE DASHBOARD DATA (JSON)
# ============================================================
print("\n" + "=" * 60)
print("PREPARING DASHBOARD DATA")
print("=" * 60)

# Orders by month for trends
orders_by_month = df.groupby('YearMonth').agg({
    'InvoiceNo': 'nunique',
    'Sales': 'sum',
    'CustomerID': 'nunique'
}).reset_index()
orders_by_month.columns = ['YearMonth', 'Orders', 'Revenue', 'Customers']
orders_by_month = orders_by_month.sort_values('YearMonth')

# Revenue by country (all)
all_countries = df.groupby('Country').agg({
    'Sales': 'sum',
    'InvoiceNo': 'nunique',
    'CustomerID': 'nunique'
}).reset_index()
all_countries.columns = ['Country', 'Revenue', 'Orders', 'Customers']
all_countries = all_countries.sort_values('Revenue', ascending=False)

# Day of week analysis
dow_analysis = df.groupby('DayOfWeek')['Sales'].sum().reset_index()
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_analysis['DayOfWeek'] = pd.Categorical(dow_analysis['DayOfWeek'], categories=dow_order, ordered=True)
dow_analysis = dow_analysis.sort_values('DayOfWeek')

# Hour analysis
hour_analysis = df.groupby('Hour')['Sales'].sum().reset_index()
hour_analysis = hour_analysis.sort_values('Hour')

# Revenue concentration (Pareto)
customer_revenue = df.groupby('CustomerID')['Sales'].sum().sort_values(ascending=False).reset_index()
customer_revenue['CumulativeRevenue'] = customer_revenue['Sales'].cumsum()
customer_revenue['CumulativePct'] = (customer_revenue['CumulativeRevenue'] / total_revenue * 100).round(2)
customer_revenue['CustomerPct'] = ((customer_revenue.index + 1) / len(customer_revenue) * 100).round(2)

# Find what % of customers generate 80% of revenue
pareto_80 = customer_revenue[customer_revenue['CumulativePct'] >= 80].iloc[0]['CustomerPct']

# Segment revenue contribution
segment_revenue = rfm.groupby('Segment').agg({
    'CustomerID': 'count',
    'Monetary': ['sum', 'mean'],
    'Recency': 'mean',
    'Frequency': 'mean'
}).reset_index()
segment_revenue.columns = ['Segment', 'CustomerCount', 'TotalRevenue', 'AvgRevenue', 'AvgRecency', 'AvgFrequency']
segment_revenue = segment_revenue.sort_values('TotalRevenue', ascending=False)

# Prepare cohort data for heatmap
cohort_heatmap = {}
for cohort in retention.index:
    cohort_heatmap[cohort] = {}
    for col in retention.columns:
        val = retention.loc[cohort, col]
        if pd.notna(val):
            cohort_heatmap[cohort][str(int(col))] = float(val)

# Build dashboard JSON
dashboard = {
    'overview': {
        'totalRevenue': round(total_revenue, 2),
        'totalOrders': int(total_orders),
        'totalCustomers': int(total_customers),
        'totalProducts': int(total_products),
        'avgOrderValue': round(avg_order_value, 2),
        'avgItemsPerOrder': round(avg_items_per_order, 1),
        'dateRange': f"{date_range_start} to {date_range_end}",
        'pareto80': round(pareto_80, 1)
    },
    'monthlyTrends': {
        'labels': orders_by_month['YearMonth'].tolist(),
        'revenue': orders_by_month['Revenue'].round(2).tolist(),
        'orders': orders_by_month['Orders'].tolist(),
        'customers': orders_by_month['Customers'].tolist()
    },
    'topProductsByRevenue': {
        'labels': top_products_rev['Description'].str[:35].tolist(),
        'values': top_products_rev['Revenue'].round(2).tolist()
    },
    'topProductsByQuantity': {
        'labels': top_products_qty['Description'].str[:35].tolist(),
        'values': top_products_qty['Quantity'].tolist()
    },
    'revenueByCountry': {
        'labels': all_countries['Country'].tolist(),
        'revenue': all_countries['Revenue'].round(2).tolist(),
        'orders': all_countries['Orders'].tolist(),
        'customers': all_countries['Customers'].tolist()
    },
    'dayOfWeek': {
        'labels': dow_analysis['DayOfWeek'].tolist(),
        'values': dow_analysis['Sales'].round(2).tolist()
    },
    'hourOfDay': {
        'labels': hour_analysis['Hour'].tolist(),
        'values': hour_analysis['Sales'].round(2).tolist()
    },
    'rfmSegments': {
        'labels': segment_revenue['Segment'].tolist(),
        'customerCount': segment_revenue['CustomerCount'].tolist(),
        'totalRevenue': segment_revenue['TotalRevenue'].round(2).tolist(),
        'avgRevenue': segment_revenue['AvgRevenue'].round(2).tolist(),
        'avgRecency': segment_revenue['AvgRecency'].round(1).tolist(),
        'avgFrequency': segment_revenue['AvgFrequency'].round(1).tolist()
    },
    'cohortRetention': cohort_heatmap,
    'topCustomers': {
        'ids': clv['CustomerID'].tolist(),
        'values': clv['LifetimeValue'].round(2).tolist()
    },
    'paretoData': {
        'customerPct': customer_revenue['CustomerPct'].head(100).tolist(),
        'revenuePct': customer_revenue['CumulativePct'].head(100).tolist()
    }
}

with open(DASHBOARD_DATA, 'w') as f:
    json.dump(dashboard, f, indent=2)

print(f"   💾 Saved dashboard data to: {DASHBOARD_DATA}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("✅ PIPELINE COMPLETE")
print("=" * 60)
print(f"   📁 Raw data:           {RAW_DATA}")
print(f"   📁 Cleaned data:       {CLEAN_DATA}")
print(f"   📁 RFM segmentation:   {rfm_output}")
print(f"   📁 Cohort retention:   {cohort_output}")
print(f"   📁 Dashboard JSON:     {DASHBOARD_DATA}")
print(f"\n   Total runtime metrics:")
print(f"   - {final_rows:,} clean transactions analyzed")
print(f"   - {total_customers:,} customers segmented")
print(f"   - {len(retention):,} monthly cohorts tracked")
print(f"   - {len(segment_dist):,} customer segments identified")

