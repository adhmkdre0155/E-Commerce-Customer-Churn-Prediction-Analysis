-- ============================================================
-- E-Commerce Customer Churn — Analysis Queries
-- Tables: transactions (line-item level), customer_rfm (one row per customer)
-- ============================================================

-- 1. Churn rate by country (min. 20 customers, to avoid noisy small-country %)
SELECT
    Country,
    COUNT(*) AS Customers,
    SUM(Churned) AS ChurnedCustomers,
    ROUND(SUM(Churned) * 100.0 / COUNT(*), 1) AS ChurnRatePct,
    ROUND(SUM(Monetary), 0) AS TotalHistoricalRevenue
FROM customer_rfm
GROUP BY Country
HAVING COUNT(*) >= 20
ORDER BY ChurnRatePct DESC;

-- 2. Churn rate and revenue at stake by RFM segment
SELECT
    Segment,
    COUNT(*) AS Customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_rfm), 1) AS PctOfCustomers,
    ROUND(AVG(Recency), 0) AS AvgRecencyDays,
    ROUND(SUM(Monetary), 0) AS TotalRevenue,
    ROUND(AVG(ChurnProbability), 3) AS AvgChurnProbability
FROM customer_rfm
GROUP BY Segment
ORDER BY TotalRevenue DESC;

-- 3. Headline query: At-Risk High Value segment detail
SELECT
    COUNT(*) AS Customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_rfm), 1) AS PctOfCustomerBase,
    ROUND(SUM(Monetary), 0) AS RevenueAtStake,
    ROUND(AVG(Recency), 0) AS AvgDaysSinceLastPurchase,
    ROUND(AVG(Frequency), 1) AS AvgHistoricalOrders
FROM customer_rfm
WHERE Segment = 'At-Risk High Value';

-- 4. Retention curve input: % of customers still active (purchased) at each
--    days-since-first-purchase bucket, using Recency as a proxy for "still active"
SELECT
    CASE
        WHEN Recency <= 30 THEN '0-30 days'
        WHEN Recency <= 60 THEN '31-60 days'
        WHEN Recency <= 90 THEN '61-90 days'
        WHEN Recency <= 180 THEN '91-180 days'
        WHEN Recency <= 270 THEN '181-270 days'
        ELSE '271+ days'
    END AS RecencyBucket,
    COUNT(*) AS Customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_rfm), 1) AS PctOfCustomers
FROM customer_rfm
GROUP BY RecencyBucket
ORDER BY MIN(Recency);

-- 5. RFM segment matrix: Recency score x Frequency score, average monetary value
SELECT
    R_Score,
    F_Score,
    COUNT(*) AS Customers,
    ROUND(AVG(Monetary), 0) AS AvgMonetary
FROM customer_rfm
GROUP BY R_Score, F_Score
ORDER BY R_Score DESC, F_Score DESC;
