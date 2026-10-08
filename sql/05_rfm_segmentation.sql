-- ============================================================
-- E-Commerce Intelligence Hub
-- 05 - RFM Customer Segmentation
-- ============================================================

-- ============================================================
-- STEP 1: Find the analysis date
-- We use the latest purchase date in the dataset as the
-- reference date for calculating customer recency.
-- ============================================================

WITH analysis_date AS (

    SELECT
        MAX(
            CAST(order_purchase_timestamp AS TIMESTAMP)
        ) AS max_purchase_date

    FROM orders
),

-- ============================================================
-- STEP 2: Calculate raw RFM metrics
-- ============================================================

customer_rfm AS (

    SELECT

        o.customer_id,

        -- Recency
        DATE_DIFF(
            'day',
            MAX(
                CAST(o.order_purchase_timestamp AS TIMESTAMP)
            ),
            a.max_purchase_date
        ) AS recency_days,

        -- Frequency
        COUNT(
            DISTINCT o.order_id
        ) AS frequency,

        -- Monetary
        SUM(
            p.payment_value
        ) AS monetary_value

    FROM orders o

    JOIN order_payments p
        ON o.order_id = p.order_id

    CROSS JOIN analysis_date a

    GROUP BY
        o.customer_id,
        a.max_purchase_date
),

-- ============================================================
-- STEP 3: Create RFM scores from 1–5
-- ============================================================

rfm_scores AS (

    SELECT

        customer_id,

        recency_days,

        frequency,

        monetary_value,

        -- Lower recency is better
        NTILE(5) OVER (
            ORDER BY recency_days DESC
        ) AS recency_score,

        -- Higher frequency is better
        NTILE(5) OVER (
            ORDER BY frequency
        ) AS frequency_score,

        -- Higher monetary value is better
        NTILE(5) OVER (
            ORDER BY monetary_value
        ) AS monetary_score

    FROM customer_rfm
),

-- ============================================================
-- STEP 4: Create combined RFM score
-- ============================================================

rfm_final AS (

    SELECT

        customer_id,

        recency_days,

        frequency,

        ROUND(
            monetary_value,
            2
        ) AS monetary_value,

        recency_score,

        frequency_score,

        monetary_score,

        (
            recency_score
            +
            frequency_score
            +
            monetary_score
        ) AS rfm_score

    FROM rfm_scores
)

-- ============================================================
-- STEP 5: Customer segments
-- ============================================================

SELECT

    customer_id,

    recency_days,

    frequency,

    monetary_value,

    recency_score,

    frequency_score,

    monetary_score,

    rfm_score,

    CASE

        WHEN rfm_score >= 13
            THEN 'Champions'

        WHEN rfm_score >= 10
            THEN 'Loyal Customers'

        WHEN rfm_score >= 8
            THEN 'Potential Loyalists'

        WHEN rfm_score >= 6
            THEN 'At Risk'

        ELSE 'Hibernating / Lost'

    END AS customer_segment

FROM rfm_final

ORDER BY rfm_score DESC, monetary_value DESC;


-- ============================================================
-- STEP 6: Segment summary
-- ============================================================

WITH analysis_date AS (

    SELECT
        MAX(
            CAST(order_purchase_timestamp AS TIMESTAMP)
        ) AS max_purchase_date

    FROM orders
),

customer_rfm AS (

    SELECT

        o.customer_id,

        DATE_DIFF(
            'day',
            MAX(
                CAST(o.order_purchase_timestamp AS TIMESTAMP)
            ),
            a.max_purchase_date
        ) AS recency_days,

        COUNT(
            DISTINCT o.order_id
        ) AS frequency,

        SUM(
            p.payment_value
        ) AS monetary_value

    FROM orders o

    JOIN order_payments p
        ON o.order_id = p.order_id

    CROSS JOIN analysis_date a

    GROUP BY
        o.customer_id,
        a.max_purchase_date
),

rfm_scores AS (

    SELECT

        customer_id,

        recency_days,

        frequency,

        monetary_value,

        NTILE(5) OVER (
            ORDER BY recency_days DESC
        ) AS recency_score,

        NTILE(5) OVER (
            ORDER BY frequency
        ) AS frequency_score,

        NTILE(5) OVER (
            ORDER BY monetary_value
        ) AS monetary_score

    FROM customer_rfm
),

rfm_segmented AS (

    SELECT

        customer_id,

        monetary_value,

        (
            recency_score
            +
            frequency_score
            +
            monetary_score
        ) AS rfm_score

    FROM rfm_scores
)

SELECT

    CASE

        WHEN rfm_score >= 13
            THEN 'Champions'

        WHEN rfm_score >= 10
            THEN 'Loyal Customers'

        WHEN rfm_score >= 8
            THEN 'Potential Loyalists'

        WHEN rfm_score >= 6
            THEN 'At Risk'

        ELSE 'Hibernating / Lost'

    END AS customer_segment,

    COUNT(*) AS customers,

    ROUND(
        SUM(monetary_value),
        2
    ) AS total_revenue,

    ROUND(
        AVG(monetary_value),
        2
    ) AS average_customer_value

FROM rfm_segmented

GROUP BY 1

ORDER BY total_revenue DESC;
