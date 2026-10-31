-- ============================================================================
-- E-Commerce Customer & Sales Analysis Queries
-- Database: SQLite
-- Table: sales
-- ============================================================================
-- Columns:
--   InvoiceNo (TEXT), StockCode (TEXT), Description (TEXT), Quantity (INTEGER),
--   InvoiceDate (TEXT), UnitPrice (REAL), CustomerID (TEXT), Country (TEXT),
--   Sales (REAL), OrderMonth (INTEGER), OrderYear (INTEGER), YearMonth (TEXT)
-- ============================================================================


-- ############################################################################
-- SECTION 1: DATA OVERVIEW
-- Quick summary statistics to understand the scope and shape of the dataset.
-- ############################################################################

-- 1a. Count total rows, unique customers, unique products, and unique invoices
SELECT
    COUNT(*)                       AS total_rows,
    COUNT(DISTINCT CustomerID)     AS unique_customers,
    COUNT(DISTINCT StockCode)      AS unique_products,
    COUNT(DISTINCT InvoiceNo)      AS unique_invoices
FROM sales;

-- 1b. Date range of the dataset (earliest and latest invoice dates)
SELECT
    MIN(InvoiceDate) AS earliest_date,
    MAX(InvoiceDate) AS latest_date
FROM sales;


-- ############################################################################
-- SECTION 2: REVENUE ANALYSIS
-- Understand total revenue, how it distributes across time and geography,
-- and how it grows month over month.
-- ############################################################################

-- 2a. Total revenue across the entire dataset
SELECT
    ROUND(SUM(Sales), 2) AS total_revenue
FROM sales;

-- 2b. Average order value (total revenue divided by unique invoices)
SELECT
    ROUND(SUM(Sales) / COUNT(DISTINCT InvoiceNo), 2) AS avg_order_value
FROM sales;

-- 2c. Revenue by month (YearMonth), ordered chronologically
SELECT
    YearMonth,
    ROUND(SUM(Sales), 2)           AS monthly_revenue,
    COUNT(DISTINCT InvoiceNo)      AS num_orders,
    COUNT(DISTINCT CustomerID)     AS num_customers
FROM sales
GROUP BY YearMonth
ORDER BY YearMonth;

-- 2d. Revenue by country, ordered by revenue descending
SELECT
    Country,
    ROUND(SUM(Sales), 2)           AS total_revenue,
    COUNT(DISTINCT InvoiceNo)      AS num_orders,
    COUNT(DISTINCT CustomerID)     AS num_customers
FROM sales
GROUP BY Country
ORDER BY total_revenue DESC;

-- 2e. Monthly revenue growth rate (percentage change from previous month)
--     Uses a CTE to compute monthly revenue, then a window function for lag.
WITH monthly_rev AS (
    SELECT
        YearMonth,
        ROUND(SUM(Sales), 2) AS revenue
    FROM sales
    GROUP BY YearMonth
    ORDER BY YearMonth
),
growth AS (
    SELECT
        YearMonth,
        revenue,
        LAG(revenue) OVER (ORDER BY YearMonth) AS prev_month_revenue
    FROM monthly_rev
)
SELECT
    YearMonth,
    revenue,
    prev_month_revenue,
    CASE
        WHEN prev_month_revenue IS NOT NULL AND prev_month_revenue != 0
        THEN ROUND((revenue - prev_month_revenue) * 100.0 / prev_month_revenue, 2)
        ELSE NULL
    END AS growth_rate_pct
FROM growth
ORDER BY YearMonth;


-- ############################################################################
-- SECTION 3: PRODUCT ANALYSIS
-- Identify best-sellers, underperformers, and product diversity over time.
-- ############################################################################

-- 3a. Top 10 products by total revenue
SELECT
    StockCode,
    Description,
    ROUND(SUM(Sales), 2)  AS total_revenue,
    SUM(Quantity)          AS total_qty_sold,
    COUNT(DISTINCT InvoiceNo) AS num_orders
FROM sales
GROUP BY StockCode, Description
ORDER BY total_revenue DESC
LIMIT 10;

-- 3b. Top 10 products by total quantity sold
SELECT
    StockCode,
    Description,
    SUM(Quantity)          AS total_qty_sold,
    ROUND(SUM(Sales), 2)  AS total_revenue
FROM sales
GROUP BY StockCode, Description
ORDER BY total_qty_sold DESC
LIMIT 10;

-- 3c. Bottom 10 products by revenue (potential underperformers)
--     Excludes products with zero or negative revenue (returns/adjustments).
SELECT
    StockCode,
    Description,
    ROUND(SUM(Sales), 2)  AS total_revenue,
    SUM(Quantity)          AS total_qty_sold
FROM sales
GROUP BY StockCode, Description
HAVING total_revenue > 0
ORDER BY total_revenue ASC
LIMIT 10;

-- 3d. Number of unique products sold per month
SELECT
    YearMonth,
    COUNT(DISTINCT StockCode) AS unique_products_sold
FROM sales
GROUP BY YearMonth
ORDER BY YearMonth;


-- ############################################################################
-- SECTION 4: CUSTOMER ANALYSIS
-- Profile customers by lifetime value, geography, purchase frequency,
-- and identify when new customers first appeared.
-- ############################################################################

-- 4a. Customers with highest lifetime value (top 20)
SELECT
    CustomerID,
    ROUND(SUM(Sales), 2)           AS lifetime_value,
    COUNT(DISTINCT InvoiceNo)      AS num_orders,
    MIN(InvoiceDate)               AS first_purchase,
    MAX(InvoiceDate)               AS last_purchase
FROM sales
WHERE CustomerID IS NOT NULL AND CustomerID != ''
GROUP BY CustomerID
ORDER BY lifetime_value DESC
LIMIT 20;

-- 4b. Customer distribution by country
SELECT
    Country,
    COUNT(DISTINCT CustomerID) AS num_customers,
    ROUND(COUNT(DISTINCT CustomerID) * 100.0 /
          (SELECT COUNT(DISTINCT CustomerID) FROM sales WHERE CustomerID IS NOT NULL AND CustomerID != ''), 2
    ) AS pct_of_total
FROM sales
WHERE CustomerID IS NOT NULL AND CustomerID != ''
GROUP BY Country
ORDER BY num_customers DESC;

-- 4c. Average revenue per customer
SELECT
    ROUND(SUM(Sales) * 1.0 / COUNT(DISTINCT CustomerID), 2) AS avg_revenue_per_customer
FROM sales
WHERE CustomerID IS NOT NULL AND CustomerID != '';

-- 4d. Customers by number of orders (frequency distribution)
--     Shows how many customers placed 1 order, 2 orders, 3 orders, etc.
WITH customer_orders AS (
    SELECT
        CustomerID,
        COUNT(DISTINCT InvoiceNo) AS order_count
    FROM sales
    WHERE CustomerID IS NOT NULL AND CustomerID != ''
    GROUP BY CustomerID
)
SELECT
    order_count                AS num_orders,
    COUNT(*)                   AS num_customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_orders), 2) AS pct_of_customers
FROM customer_orders
GROUP BY order_count
ORDER BY order_count;

-- 4e. New customers per month (first purchase in that month)
WITH first_purchase AS (
    SELECT
        CustomerID,
        MIN(YearMonth) AS cohort_month
    FROM sales
    WHERE CustomerID IS NOT NULL AND CustomerID != ''
    GROUP BY CustomerID
)
SELECT
    cohort_month,
    COUNT(*) AS new_customers
FROM first_purchase
GROUP BY cohort_month
ORDER BY cohort_month;


-- ############################################################################
-- SECTION 5: RFM ANALYSIS
-- Segment customers by Recency, Frequency, and Monetary value.
-- ############################################################################

-- 5a. Calculate raw RFM values for each customer
--     Recency  = days between max date in dataset and customer's last purchase
--     Frequency = count of distinct invoices per customer
--     Monetary  = total sales per customer
WITH rfm_raw AS (
    SELECT
        CustomerID,
        -- Recency: days since last purchase relative to the dataset's max date
        CAST(
            julianday((SELECT MAX(InvoiceDate) FROM sales))
            - julianday(MAX(InvoiceDate))
        AS INTEGER) AS recency,
        COUNT(DISTINCT InvoiceNo) AS frequency,
        ROUND(SUM(Sales), 2)      AS monetary
    FROM sales
    WHERE CustomerID IS NOT NULL AND CustomerID != ''
    GROUP BY CustomerID
),

-- 5b. Assign R, F, M scores (1-5) using NTILE quintiles
--     Higher R score = more recent (lower recency days)
--     Higher F score = more frequent
--     Higher M score = higher monetary value
rfm_scores AS (
    SELECT
        CustomerID,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,  -- lower recency = higher score
        NTILE(5) OVER (ORDER BY frequency ASC)  AS f_score,  -- higher frequency = higher score
        NTILE(5) OVER (ORDER BY monetary ASC)   AS m_score   -- higher monetary = higher score
    FROM rfm_raw
    WHERE monetary > 0  -- exclude negative-value customers (returns only)
)

-- 5c. Create RFM segments using CASE statements
SELECT
    CustomerID,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4
            THEN 'Champions'
        WHEN f_score >= 3 AND m_score >= 3
            THEN 'Loyal Customers'
        WHEN r_score >= 3 AND f_score >= 2
            THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 2
            THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2
            THEN 'Lost Customers'
        ELSE 'Others'
    END AS rfm_segment
FROM rfm_scores
ORDER BY rfm_total DESC;

-- 5d. Summary: count and average monetary value per RFM segment
WITH rfm_raw AS (
    SELECT
        CustomerID,
        CAST(
            julianday((SELECT MAX(InvoiceDate) FROM sales))
            - julianday(MAX(InvoiceDate))
        AS INTEGER) AS recency,
        COUNT(DISTINCT InvoiceNo) AS frequency,
        ROUND(SUM(Sales), 2)      AS monetary
    FROM sales
    WHERE CustomerID IS NOT NULL AND CustomerID != ''
    GROUP BY CustomerID
),
rfm_scores AS (
    SELECT
        CustomerID, recency, frequency, monetary,
        NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)  AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)   AS m_score
    FROM rfm_raw
    WHERE monetary > 0
),
rfm_segments AS (
    SELECT
        *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN f_score >= 3 AND m_score >= 3                  THEN 'Loyal Customers'
            WHEN r_score >= 3 AND f_score >= 2                  THEN 'Potential Loyalists'
            WHEN r_score <= 2 AND f_score >= 2                  THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Lost Customers'
            ELSE 'Others'
        END AS rfm_segment
    FROM rfm_scores
)
SELECT
    rfm_segment,
    COUNT(*)                       AS num_customers,
    ROUND(AVG(monetary), 2)        AS avg_monetary,
    ROUND(AVG(frequency), 2)       AS avg_frequency,
    ROUND(AVG(recency), 2)         AS avg_recency,
    ROUND(SUM(monetary), 2)        AS total_revenue
FROM rfm_segments
GROUP BY rfm_segment
ORDER BY total_revenue DESC;


-- ############################################################################
-- SECTION 6: COHORT RETENTION ANALYSIS
-- Track how well each monthly cohort of customers is retained over time.
-- ############################################################################

-- 6a. Find each customer's cohort (first purchase month) and calculate
--     cohort index (months since first purchase) for every transaction.
WITH customer_cohort AS (
    -- Each customer's first purchase month defines their cohort
    SELECT
        CustomerID,
        MIN(YearMonth) AS cohort_month
    FROM sales
    WHERE CustomerID IS NOT NULL AND CustomerID != ''
    GROUP BY CustomerID
),
transactions_with_cohort AS (
    -- Join cohort info back to every transaction
    SELECT
        s.CustomerID,
        s.YearMonth                AS transaction_month,
        c.cohort_month,
        -- Calculate months between cohort month and transaction month
        -- YearMonth format assumed to be 'YYYY-MM'
        (CAST(SUBSTR(s.YearMonth, 1, 4) AS INTEGER) - CAST(SUBSTR(c.cohort_month, 1, 4) AS INTEGER)) * 12
        + (CAST(SUBSTR(s.YearMonth, 6, 2) AS INTEGER) - CAST(SUBSTR(c.cohort_month, 6, 2) AS INTEGER))
        AS cohort_index
    FROM sales s
    JOIN customer_cohort c ON s.CustomerID = c.CustomerID
),

-- 6b. Build cohort retention table: count distinct customers per cohort per period
cohort_counts AS (
    SELECT
        cohort_month,
        cohort_index,
        COUNT(DISTINCT CustomerID) AS num_customers
    FROM transactions_with_cohort
    GROUP BY cohort_month, cohort_index
),

-- Get the initial size of each cohort (cohort_index = 0)
cohort_sizes AS (
    SELECT
        cohort_month,
        num_customers AS cohort_size
    FROM cohort_counts
    WHERE cohort_index = 0
)

-- 6c. Calculate retention rates as percentages
SELECT
    cc.cohort_month,
    cs.cohort_size,
    cc.cohort_index,
    cc.num_customers                                          AS retained_customers,
    ROUND(cc.num_customers * 100.0 / cs.cohort_size, 2)       AS retention_rate_pct
FROM cohort_counts cc
JOIN cohort_sizes cs ON cc.cohort_month = cs.cohort_month
ORDER BY cc.cohort_month, cc.cohort_index;


-- ############################################################################
-- SECTION 7: ADVANCED INSIGHTS
-- Deeper analytical queries for strategic decision-making.
-- ############################################################################

-- 7a. Revenue concentration – Pareto analysis
--     What percentage of customers generate 80% of total revenue?
WITH customer_revenue AS (
    SELECT
        CustomerID,
        ROUND(SUM(Sales), 2) AS total_revenue
    FROM sales
    WHERE CustomerID IS NOT NULL AND CustomerID != ''
    GROUP BY CustomerID
    HAVING total_revenue > 0
),
ranked AS (
    SELECT
        CustomerID,
        total_revenue,
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC) AS cumulative_revenue,
        (SELECT SUM(total_revenue) FROM customer_revenue)     AS grand_total,
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC)       AS customer_rank,
        (SELECT COUNT(*) FROM customer_revenue)               AS total_customers
    FROM customer_revenue
)
SELECT
    customer_rank,
    CustomerID,
    total_revenue,
    ROUND(cumulative_revenue, 2)                              AS cumulative_revenue,
    ROUND(cumulative_revenue * 100.0 / grand_total, 2)        AS cumulative_pct,
    ROUND(customer_rank * 100.0 / total_customers, 2)         AS customer_pct
FROM ranked
-- Show the cutoff point where cumulative revenue first exceeds 80%
WHERE cumulative_revenue <= grand_total * 0.8
   OR customer_rank = (
        SELECT MIN(r2.customer_rank)
        FROM ranked r2
        WHERE r2.cumulative_revenue >= grand_total * 0.8
   )
ORDER BY customer_rank;

-- 7a-summary. Pareto summary: what % of customers drive 80% of revenue
WITH customer_revenue AS (
    SELECT
        CustomerID,
        ROUND(SUM(Sales), 2) AS total_revenue
    FROM sales
    WHERE CustomerID IS NOT NULL AND CustomerID != ''
    GROUP BY CustomerID
    HAVING total_revenue > 0
),
ranked AS (
    SELECT
        CustomerID,
        total_revenue,
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC) AS cumulative_revenue,
        (SELECT SUM(total_revenue) FROM customer_revenue)     AS grand_total,
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC)       AS customer_rank,
        (SELECT COUNT(*) FROM customer_revenue)               AS total_customers
    FROM customer_revenue
)
SELECT
    MIN(customer_rank) AS customers_needed_for_80pct,
    (SELECT COUNT(*) FROM customer_revenue) AS total_customers,
    ROUND(MIN(customer_rank) * 100.0 / (SELECT COUNT(*) FROM customer_revenue), 2)
        AS pct_customers_for_80pct_revenue
FROM ranked
WHERE cumulative_revenue >= grand_total * 0.8;

-- 7b. Average basket size (number of distinct items per order)
SELECT
    ROUND(AVG(items_per_order), 2) AS avg_basket_size
FROM (
    SELECT
        InvoiceNo,
        COUNT(DISTINCT StockCode) AS items_per_order
    FROM sales
    GROUP BY InvoiceNo
);

-- 7c. Best day of week for sales
--     SQLite's strftime('%w', ...) returns 0=Sunday through 6=Saturday.
SELECT
    CASE CAST(strftime('%w', InvoiceDate) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_of_week,
    CAST(strftime('%w', InvoiceDate) AS INTEGER) AS day_num,
    ROUND(SUM(Sales), 2)          AS total_revenue,
    COUNT(DISTINCT InvoiceNo)     AS num_orders,
    ROUND(SUM(Sales) / COUNT(DISTINCT InvoiceNo), 2) AS avg_order_value
FROM sales
GROUP BY day_num
ORDER BY total_revenue DESC;

-- 7d. Revenue by hour of day
--     Extracts hour from InvoiceDate (assumes datetime format like 'YYYY-MM-DD HH:MM:SS'
--     or 'MM/DD/YYYY HH:MM'). Uses strftime for robust extraction.
SELECT
    CAST(strftime('%H', InvoiceDate) AS INTEGER) AS hour_of_day,
    ROUND(SUM(Sales), 2)                         AS total_revenue,
    COUNT(DISTINCT InvoiceNo)                    AS num_orders,
    COUNT(DISTINCT CustomerID)                   AS num_customers
FROM sales
WHERE strftime('%H', InvoiceDate) IS NOT NULL
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- ============================================================================
-- END OF ANALYSIS QUERIES
-- ============================================================================
