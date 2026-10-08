-- ============================================================
-- E-Commerce Intelligence Hub
-- 04 - Product Analytics
-- ============================================================


-- ============================================================
-- 1. REVENUE BY PRODUCT CATEGORY
-- ============================================================

SELECT

    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,

    COUNT(DISTINCT oi.order_id) AS orders,

    SUM(oi.order_item_id) AS units_sold,

    ROUND(
        SUM(oi.price),
        2
    ) AS product_revenue

FROM order_items oi

JOIN products p
    ON oi.product_id = p.product_id

LEFT JOIN product_category_translation t
    ON p.product_category_name =
       t.product_category_name

GROUP BY 1

ORDER BY product_revenue DESC;


-- ============================================================
-- 2. TOP 20 PRODUCTS BY REVENUE
-- ============================================================

SELECT

    oi.product_id,

    COUNT(DISTINCT oi.order_id) AS orders,

    SUM(oi.order_item_id) AS units_sold,

    ROUND(
        SUM(oi.price),
        2
    ) AS revenue

FROM order_items oi

GROUP BY oi.product_id

ORDER BY revenue DESC

LIMIT 20;


-- ============================================================
-- 3. CATEGORY REVENUE CONTRIBUTION
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

    ROUND(
        100.0 * revenue /
        SUM(revenue) OVER (),
        2
    ) AS revenue_share_pct

FROM category_revenue

ORDER BY revenue DESC;


-- ============================================================
-- 4. CATEGORY RANKING
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
    ) AS revenue_rank

FROM category_revenue

ORDER BY revenue_rank;


-- ============================================================
-- 5. AVERAGE PRODUCT PRICE BY CATEGORY
-- ============================================================

SELECT

    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,

    COUNT(*) AS items_sold,

    ROUND(
        AVG(oi.price),
        2
    ) AS average_price

FROM order_items oi

JOIN products p
    ON oi.product_id = p.product_id

LEFT JOIN product_category_translation t
    ON p.product_category_name =
       t.product_category_name

GROUP BY 1

HAVING COUNT(*) >= 100

ORDER BY average_price DESC;
