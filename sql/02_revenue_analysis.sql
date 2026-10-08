-- ============================================================
-- E-Commerce Intelligence Hub
-- 02 - Revenue Analysis
-- ============================================================

-- 1. Overall revenue
SELECT
    ROUND(SUM(payment_value), 2) AS total_revenue
FROM order_payments;


-- 2. Total number of orders
SELECT
    COUNT(DISTINCT order_id) AS total_orders
FROM orders;


-- 3. Average order value
SELECT
    ROUND(AVG(order_total), 2) AS average_order_value
FROM (
    SELECT
        order_id,
        SUM(payment_value) AS order_total
    FROM order_payments
    GROUP BY order_id
);


-- 4. Monthly revenue
SELECT
    DATE_TRUNC(
        'month',
        CAST(order_purchase_timestamp AS TIMESTAMP)
    ) AS month,
    ROUND(SUM(p.payment_value), 2) AS revenue
FROM orders o
JOIN order_payments p
    ON o.order_id = p.order_id
GROUP BY 1
ORDER BY 1;


-- 5. Monthly revenue growth
WITH monthly_revenue AS (

    SELECT
        DATE_TRUNC(
            'month',
            CAST(o.order_purchase_timestamp AS TIMESTAMP)
        ) AS month,

        SUM(p.payment_value) AS revenue

    FROM orders o

    JOIN order_payments p
        ON o.order_id = p.order_id

    GROUP BY 1
)

SELECT
    month,
    ROUND(revenue, 2) AS revenue,

    ROUND(
        LAG(revenue) OVER (
            ORDER BY month
        ),
        2
    ) AS previous_month_revenue,

    ROUND(
        100.0 *
        (
            revenue
            -
            LAG(revenue) OVER (
                ORDER BY month
            )
        )
        /
        NULLIF(
            LAG(revenue) OVER (
                ORDER BY month
            ),
            0
        ),
        2
    ) AS revenue_growth_pct

FROM monthly_revenue

ORDER BY month;
