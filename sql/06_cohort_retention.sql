-- ============================================================
-- E-Commerce Intelligence Hub
-- 06 - Customer Cohort Retention
-- ============================================================

-- ============================================================
-- 1. Assign every customer to their first-purchase cohort
-- ============================================================

WITH customer_first_purchase AS (

    SELECT
        customer_id,

        DATE_TRUNC(
            'month',
            MIN(
                CAST(order_purchase_timestamp AS TIMESTAMP)
            )
        ) AS cohort_month

    FROM orders

    GROUP BY customer_id
),

-- ============================================================
-- 2. Get every customer's purchase month
-- ============================================================

customer_activity AS (

    SELECT DISTINCT

        o.customer_id,

        DATE_TRUNC(
            'month',
            CAST(o.order_purchase_timestamp AS TIMESTAMP)
        ) AS purchase_month

    FROM orders o
),

-- ============================================================
-- 3. Calculate months since first purchase
-- ============================================================

cohort_activity AS (

    SELECT

        f.cohort_month,

        a.purchase_month,

        DATE_DIFF(
            'month',
            f.cohort_month,
            a.purchase_month
        ) AS months_since_first_purchase,

        a.customer_id

    FROM customer_first_purchase f

    JOIN customer_activity a
        ON f.customer_id = a.customer_id
),

-- ============================================================
-- 4. Count active customers in each cohort/month
-- ============================================================

cohort_counts AS (

    SELECT

        cohort_month,

        months_since_first_purchase,

        COUNT(DISTINCT customer_id) AS active_customers

    FROM cohort_activity

    GROUP BY
        cohort_month,
        months_since_first_purchase
),

-- ============================================================
-- 5. Calculate original cohort size
-- ============================================================

cohort_sizes AS (

    SELECT

        cohort_month,

        MAX(
            CASE
                WHEN months_since_first_purchase = 0
                THEN active_customers
            END
        ) AS cohort_size

    FROM cohort_counts

    GROUP BY cohort_month
)

-- ============================================================
-- 6. Final retention table
-- ============================================================

SELECT

    c.cohort_month,

    c.months_since_first_purchase,

    c.active_customers,

    s.cohort_size,

    ROUND(

        100.0 *
        c.active_customers /
        NULLIF(s.cohort_size, 0),

        2

    ) AS retention_rate_pct

FROM cohort_counts c

JOIN cohort_sizes s
    ON c.cohort_month = s.cohort_month

ORDER BY

    c.cohort_month,
    c.months_since_first_purchase;
