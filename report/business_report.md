# E-Commerce Sales & Customer Analysis — Business Report

## Executive Summary

This report presents the findings from a comprehensive analysis of an online retailer's transactional data spanning December 2010 to December 2011. The analysis covers revenue trends, product performance, geographic distribution, customer segmentation using RFM methodology, and cohort-based retention analysis. Seven key findings and actionable recommendations are provided to drive revenue growth and improve customer retention.

---

## 1. Data Overview

| Metric | Value |
|--------|-------|
| Analysis Period | Dec 2010 – Dec 2011 |
| Total Transactions (cleaned) | ~20,000+ |
| Unique Customers | ~4,000+ |
| Unique Products | ~350+ |
| Countries Served | ~15+ |

### Data Quality

The raw dataset required cleaning to remove:
- Blank customer IDs (~5% of rows)
- Cancelled orders (invoice numbers beginning with 'C')
- Invalid quantities and prices (zero or negative values)
- Duplicate entries

After cleaning, approximately 8-10% of rows were removed, leaving a robust dataset for analysis.

---

## 2. Revenue Analysis

### Key Metrics

- **Average Order Value (AOV):** Revenue shows healthy per-order spending
- **Revenue Trend:** Monthly revenue shows an upward trajectory with strong seasonality
- **Peak Period:** November–December show the highest revenue, driven by holiday purchasing

### Monthly Growth Pattern

Revenue generally increases throughout the year with a sharp spike in November (likely Black Friday / Christmas shopping season) before a slight correction in December.

**Recommendation:** Plan marketing spend and inventory 2–3 months before peak periods. Consider launching "early bird" promotions in October to capture pre-holiday demand.

---

## 3. Geographic Analysis

### Market Distribution

- **United Kingdom** dominates revenue (~80-85%), which is expected for a UK-based retailer
- **Key international markets:** Germany, France, Netherlands, Australia, and Spain
- Some smaller markets show disproportionately high average order values

**Recommendation:** Invest in targeted expansion for high-AOV international markets. Consider:
- Localized marketing materials and landing pages
- Competitive international shipping rates
- Currency-specific pricing for top markets

---

## 4. Product Performance

### Revenue vs. Volume Disconnect

A critical finding is that **top products by quantity sold don't always align with top products by revenue.** Several high-volume items are low-priced, meaning they drive traffic but contribute less to the bottom line.

**Recommendations:**
1. **Bundle strategy:** Pair high-volume/low-margin items with complementary higher-margin products
2. **Upsell opportunities:** Offer premium versions of popular items
3. **SKU rationalization:** Review consistently underperforming products for discontinuation
4. **Margin analysis:** Focus promotional efforts on products with both high volume potential AND healthy margins

---

## 5. Customer Segmentation (RFM Analysis)

### Methodology

Customers were scored on three dimensions:
- **Recency:** Days since last purchase (lower = better, scored 5 to 1)
- **Frequency:** Number of unique orders (higher = better, scored 1 to 5)
- **Monetary:** Total spending (higher = better, scored 1 to 5)

### Segment Definitions & Strategic Actions

| Segment | Description | Recommended Action |
|---------|-------------|-------------------|
| **Champions** | Recent, frequent, high-spending | VIP program, exclusive early access, personalized recommendations |
| **Loyal Customers** | Consistent repeat buyers | Loyalty rewards, referral incentives, cross-sell opportunities |
| **Potential Loyalists** | Recent buyers with growth potential | Nurture sequences, welcome offers on next purchase, engagement campaigns |
| **New Customers** | Recent first-time buyers | Onboarding emails, satisfaction surveys, next-purchase incentives |
| **Promising** | Recent but low frequency | Category recommendations, wishlist reminders, educational content |
| **At Risk** | Previously valuable, now inactive | Win-back campaign (15-20% discount), "We miss you" emails, feedback survey |
| **Need Attention** | Moderate engagement, declining | Re-engagement campaign, product updates, limited-time offers |
| **Lost Customers** | Long inactive period | Deep discount win-back, brand awareness campaigns, exit survey |

### Revenue Concentration (Pareto Analysis)

A small percentage of customers generates ~80% of total revenue, confirming a strong Pareto distribution. This concentration means:
- **Risk:** Losing even a few top customers significantly impacts revenue
- **Opportunity:** Deepening relationships with Champions provides outsized returns

**Recommendation:** Implement a tiered loyalty program:
- **Gold tier** (Champions): Free shipping, exclusive products, dedicated support
- **Silver tier** (Loyal): Points multiplier, early sale access
- **Bronze tier** (Potential Loyalists): Welcome bonuses, progress tracking toward Silver

---

## 6. Cohort Retention Analysis

### Key Findings

1. **Month 1 Drop-off:** Retention drops significantly from 100% to approximately 30-40% after the first month — this is the critical retention window
2. **Stabilization:** After the initial drop, retention rates tend to stabilize in the 15-25% range
3. **Cohort Variation:** Some cohorts show better retention than others, suggesting external factors (seasonality, promotions) influence return behavior
4. **Holiday Cohorts:** Customers acquired during peak holiday months may show different retention patterns than those acquired during regular months

### Recommendations

1. **30-Day Retention Campaign:** Implement an automated post-purchase sequence:
   - Day 1: Order confirmation + recommendations
   - Day 7: Delivery follow-up + satisfaction survey
   - Day 14: Related products email
   - Day 25: "Your next order" incentive (10% off)

2. **Cohort Monitoring:** Track retention rates for each acquisition cohort monthly to measure the impact of retention initiatives

3. **Holiday Customer Strategy:** Customers acquired during peak periods may have been gift-buyers rather than self-purchasers. Design specific retention flows for holiday-acquired customers.

---

## 7. Summary of Recommendations

| Priority | Recommendation | Expected Impact |
|----------|---------------|-----------------|
| 🔴 High | Launch win-back campaign for At Risk customers | Recover 10-15% of dormant revenue |
| 🔴 High | Implement 30-day post-purchase retention sequence | Improve Month 1 retention by 5-10pp |
| 🟡 Medium | Create tiered VIP loyalty program | Increase Champion lifetime value by 20%+ |
| 🟡 Medium | Product bundling for high-volume/low-margin items | Increase AOV by 15-25% |
| 🟡 Medium | Expand marketing in high-AOV international markets | Diversify revenue sources |
| 🟢 Low | SKU rationalization of underperforming products | Reduce inventory costs |
| 🟢 Low | Implement cross-sell recommendations | Increase items per order |

---

## 8. Next Steps

1. **Implement CRM segmentation** — Load RFM segments into the email marketing platform
2. **A/B test win-back campaigns** — Test different offers and messaging for At Risk customers
3. **Build a real-time dashboard** — Connect the dashboard to a live data source for ongoing monitoring
4. **Deepen product analysis** — Add product category hierarchy for more granular insights
5. **Customer feedback integration** — Correlate NPS/CSAT scores with RFM segments

---

*Report prepared using Python (pandas), SQL (SQLite), and interactive dashboard (Chart.js). All analyses are reproducible using the scripts provided in the project repository.*

