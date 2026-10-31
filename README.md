# 📊 E-Commerce Customer Analysis

> Sales Analytics, Customer Segmentation (RFM) & Cohort Retention Analysis

## 🎯 Business Problem

An online retailer needs to understand their revenue trends, customer behavior, product performance, and retention patterns. This project analyzes transactional data to answer critical business questions and provide actionable recommendations for growth.

## 📁 Project Structure

```
ecommerce-customer-analysis/
├── data/
│   ├── raw_data.csv              # Original transactional data (~25,000 rows)
│   ├── cleaned_data.csv          # Cleaned & enriched dataset
│   ├── rfm_segmentation.csv      # RFM scores & segments per customer
│   └── cohort_retention.csv      # Monthly cohort retention rates
├── sql/
│   └── analysis_queries.sql      # 7 sections of analytical SQL queries
├── scripts/
│   ├── generate_data.py          # Data generation script
│   └── clean_and_analyze.py      # Cleaning, RFM, cohort & export pipeline
├── dashboard/
│   ├── ecommerce_dashboard.html  # Interactive HTML dashboard (Chart.js)
│   └── dashboard_data.json       # Dashboard data feed
├── report/
│   └── business_report.md        # Detailed findings & recommendations
└── README.md                     # This file
```

## 🧹 Data Cleaning Process

1. **Removed blank CustomerIDs** — transactions without customer attribution are unusable for segmentation
2. **Removed cancelled orders** — invoices starting with 'C' represent cancellations/returns
3. **Removed invalid quantities & prices** — zero or negative values indicate data errors or returns
4. **Created `Sales` column** — `Quantity × UnitPrice` for revenue calculations
5. **Added date dimensions** — `OrderMonth`, `OrderYear`, `YearMonth` for time-series analysis
6. **Handled duplicates** — removed exact duplicate rows
7. **Filled missing descriptions** — replaced NaN product descriptions with 'Unknown Product'

## 📈 Key Analyses

### Core Business Metrics
- Total revenue, orders, customers, average order value
- Revenue trends by month, country, and product
- Customer lifetime value rankings

### RFM Customer Segmentation
| Metric | Description |
|--------|-------------|
| **Recency** | Days since customer's last purchase |
| **Frequency** | Number of unique orders |
| **Monetary** | Total spending |

Customers are scored 1–5 on each dimension and classified into segments:
- 🏆 **Champions** — Recent, frequent, high-spending
- 💙 **Loyal Customers** — Consistent repeat buyers
- 🌱 **Potential Loyalists** — Recent buyers showing promise
- ⚠️ **At Risk** — Previously valuable, now dormant
- ❌ **Lost Customers** — Long-inactive customers

### Cohort Retention Analysis
- Each customer is assigned to their **first purchase month** (cohort)
- Retention rates show what percentage of each cohort returned in subsequent months
- Visualized as an interactive heatmap in the dashboard

## 🖥️ Dashboard

The interactive HTML dashboard includes:

1. **Overview** — KPI cards with revenue, orders, customers, AOV
2. **Sales Trends** — Monthly revenue line chart, orders bar chart, day-of-week & hourly analysis
3. **Products** — Top 10 products by revenue and quantity (horizontal bar charts)
4. **Geography** — Revenue by country with detailed table
5. **Customers & RFM** — Segment distribution donut, revenue by segment, Pareto curve
6. **Cohort Retention** — Color-coded heatmap showing retention rates over time
7. **Insights** — 7 data-driven business recommendations

### How to View the Dashboard

```bash
cd dashboard/
python -m http.server 8080
```
Then open `http://localhost:8080/ecommerce_dashboard.html` in your browser.

## 🔍 SQL Queries

The `sql/analysis_queries.sql` file contains 7 sections of SQLite-compatible queries:
1. Data Overview
2. Revenue Analysis (with monthly growth rates)
3. Product Analysis (top/bottom performers)
4. Customer Analysis (LTV, frequency distribution)
5. RFM Segmentation (NTILE scoring, CASE segmentation)
6. Cohort Retention (CTE-based retention calculation)
7. Advanced Insights (Pareto analysis, basket size, temporal patterns)

## 💡 Key Findings

1. **Revenue is highly concentrated** — a small percentage of customers generates the majority of revenue (Pareto principle)
2. **Strong seasonal patterns** — November/December show peak revenue driven by holiday shopping
3. **The UK dominates** — but European markets show strong average order values worth expanding into
4. **Retention drops sharply after Month 1** — the critical retention window is the first 30 days
5. **High-volume ≠ High-revenue** — some best-selling products by quantity contribute relatively low revenue
6. **At-risk customers represent recoverable revenue** — targeted win-back campaigns could recover significant value
7. **Average order value can be optimized** — cross-sell and bundling strategies could increase basket size 15-25%

## 🛠️ Technologies Used

- **Python** (pandas, numpy) — Data generation, cleaning, analysis
- **SQL** (SQLite) — Analytical queries
- **HTML/CSS/JavaScript** (Chart.js) — Interactive dashboard
- **RFM Analysis** — Customer segmentation methodology
- **Cohort Analysis** — Retention measurement framework

## 🚀 How to Reproduce

```bash
# 1. Generate the dataset
python scripts/generate_data.py

# 2. Clean, analyze, and export dashboard data
python scripts/clean_and_analyze.py

# 3. Launch the dashboard
cd dashboard && python -m http.server 8080
```

---

*Built as a data analytics portfolio project demonstrating end-to-end skills in data cleaning, SQL analysis, customer segmentation, cohort retention analysis, and interactive dashboard design.*

