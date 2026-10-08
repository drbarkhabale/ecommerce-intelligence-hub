-- ============================================================
-- E-Commerce Intelligence Hub
-- 03 - Customer Analytics
-- ============================================================


-- ============================================================
-- 1. CUSTOMER ORDER SUMMARY
-- ============================================================

WITH customer_orders AS (

    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS total_orders,
        MIN(order_purchase_timestamp) AS first_purchase,
        MAX(order_purchase_timestamp) AS latest_purchase

    FROM orders

    GROUP BY customer_id
)

SELECT
    customer_id,
    total_orders,
    first_purchase,
    latest_purchase

FROM customer_orders

ORDER BY total_orders DESC;


-- ============================================================
-- 2. CUSTOMER SPENDING
-- ============================================================

WITH customer_spend AS (

    SELECT
        o.customer_id,
        SUM(p.payment_value) AS total_spend,
        COUNT(DISTINCT o.order_id) AS total_orders

    FROM orders o

    JOIN order_payments p
        ON o.order_id = p.order_id

    GROUP BY o.customer_id
)

SELECT
    customer_id,
    total_orders,
    ROUND(total_spend, 2) AS total_spend,
    ROUND(
        total_spend / NULLIF(total_orders, 0),
        2
    ) AS average_order_value

FROM customer_spend

ORDER BY total_spend DESC;


-- ============================================================
-- 3. CUSTOMER SEGMENTATION
-- ============================================================

WITH customer_metrics AS (

    SELECT
        o.customer_id,

        COUNT(DISTINCT o.order_id) AS total_orders,

        SUM(p.payment_value) AS total_spend,

        AVG(p.payment_value) AS average_payment

    FROM orders o

    JOIN order_payments p
        ON o.order_id = p.order_id

    GROUP BY o.customer_id
)

SELECT
    customer_id,
    total_orders,
    ROUND(total_spend, 2) AS total_spend,
    ROUND(average_payment, 2) AS average_payment,

    CASE

        WHEN total_orders >= 5
             AND total_spend >= 500
            THEN 'High Value'

        WHEN total_orders >= 2
             AND total_spend >= 200
            THEN 'Loyal'

        WHEN total_orders = 1
             AND total_spend >= 200
            THEN 'High Value One-Time'

        ELSE 'Standard'

    END AS customer_segment

FROM customer_metrics

ORDER BY total_spend DESC;


-- ============================================================
-- 4. REPEAT PURCHASE ANALYSIS
-- ============================================================

WITH customer_orders AS (

    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count

    FROM orders

    GROUP BY customer_id
)

SELECT

    COUNT(*) AS total_customers,

    COUNT(
        CASE
            WHEN order_count = 1 THEN 1
        END
    ) AS one_time_customers,

    COUNT(
        CASE
            WHEN order_count > 1 THEN 1
        END
    ) AS repeat_customers,

    ROUND(
        100.0 *
        COUNT(
            CASE
                WHEN order_count > 1 THEN 1
            END
        )
        / COUNT(*),
        2
    ) AS repeat_customer_rate_pct

FROM customer_orders;


-- ============================================================
-- 5. TOP 20 CUSTOMERS BY SPEND
-- ============================================================

SELECT
    o.customer_id,

    COUNT(DISTINCT o.order_id) AS total_orders,

    ROUND(
        SUM(p.payment_value),
        2
    ) AS total_spend

FROM orders o

JOIN order_payments p
    ON o.order_id = p.order_id

GROUP BY o.customer_id

ORDER BY total_spend DESC

LIMIT 20;
