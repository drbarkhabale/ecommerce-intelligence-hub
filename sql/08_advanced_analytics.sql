-- ============================================================
-- E-Commerce Intelligence Hub
-- 08 - Advanced SQL Analytics
-- ============================================================

-- ============================================================
-- 1. Monthly revenue with cumulative revenue
-- ============================================================

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

        SUM(revenue) OVER (
            ORDER BY month
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ),

        2

    ) AS cumulative_revenue,

    ROUND(

        100.0 *
        revenue /
        SUM(revenue) OVER (),

        2

    ) AS revenue_share_pct

FROM monthly_revenue

ORDER BY month;


-- ============================================================
-- 2. Monthly active customers
-- ============================================================

SELECT

    DATE_TRUNC(
        'month',
        CAST(order_purchase_timestamp AS TIMESTAMP)
    ) AS month,

    COUNT(
        DISTINCT customer_id
    ) AS active_customers,

    COUNT(
        DISTINCT order_id
    ) AS orders

FROM orders

GROUP BY 1

ORDER BY 1;


-- ============================================================
-- 3. Customer revenue ranking
-- ============================================================

WITH customer_revenue AS (

    SELECT

        o.customer_id,

        SUM(p.payment_value) AS revenue

    FROM orders o

    JOIN order_payments p
        ON o.order_id = p.order_id

    GROUP BY o.customer_id
)

SELECT

    customer_id,

    ROUND(revenue, 2) AS revenue,

    RANK() OVER (
        ORDER BY revenue DESC
    ) AS revenue_rank,

    ROUND(

        PERCENT_RANK() OVER (
            ORDER BY revenue
        ),

        4

    ) AS percentile_rank

FROM customer_revenue

ORDER BY revenue DESC

LIMIT 50;


-- ============================================================
-- 4. Category ranking within overall product revenue
-- ============================================================

WITH category_revenue AS (

    SELECT

        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'Unknown'
        ) AS category,

        SUM(oi.price) AS revenue

    FROM order_items oi

    JOIN products p
        ON oi.product_id = p.product_id

    LEFT JOIN product_category_translation t
        ON p.product_category_name =
           t.product_category_name

    GROUP BY 1
)

SELECT

    category,

    ROUND(revenue, 2) AS revenue,

    RANK() OVER (
        ORDER BY revenue DESC
    ) AS category_rank,

    ROUND(

        100.0 *
        revenue /
        SUM(revenue) OVER (),

        2

    ) AS revenue_share_pct

FROM category_revenue

ORDER BY category_rank;


-- ============================================================
-- 5. Monthly order growth
-- ============================================================

WITH monthly_orders AS (

    SELECT

        DATE_TRUNC(
            'month',
            CAST(order_purchase_timestamp AS TIMESTAMP)
        ) AS month,

        COUNT(
            DISTINCT order_id
        ) AS orders

    FROM orders

    GROUP BY 1
)

SELECT

    month,

    orders,

    LAG(orders) OVER (
        ORDER BY month
    ) AS previous_month_orders,

    ROUND(

        100.0 *
        (
            orders -
            LAG(orders) OVER (
                ORDER BY month
            )
        )
        /
        NULLIF(
            LAG(orders) OVER (
                ORDER BY month
            ),
            0
        ),

        2

    ) AS order_growth_pct

FROM monthly_orders

ORDER BY month;
