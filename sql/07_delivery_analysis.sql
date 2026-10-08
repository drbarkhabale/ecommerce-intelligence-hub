-- ============================================================
-- E-Commerce Intelligence Hub
-- 07 - Delivery Performance & Customer Satisfaction
-- ============================================================

-- ============================================================
-- 1. Delivery performance
-- ============================================================

WITH delivery_metrics AS (

    SELECT

        order_id,

        order_status,

        CAST(
            order_purchase_timestamp AS TIMESTAMP
        ) AS purchase_date,

        CAST(
            order_delivered_customer_date AS TIMESTAMP
        ) AS delivered_date,

        CAST(
            order_estimated_delivery_date AS TIMESTAMP
        ) AS estimated_date

    FROM orders

    WHERE order_delivered_customer_date IS NOT NULL

)

SELECT

    order_id,

    order_status,

    DATE_DIFF(
        'day',
        purchase_date,
        delivered_date
    ) AS delivery_days,

    DATE_DIFF(
        'day',
        estimated_date,
        delivered_date
    ) AS days_vs_estimate,

    CASE

        WHEN delivered_date <= estimated_date
            THEN 'On Time'

        ELSE 'Late'

    END AS delivery_status

FROM delivery_metrics

ORDER BY delivery_days DESC;


-- ============================================================
-- 2. Overall delivery performance
-- ============================================================

WITH delivery_metrics AS (

    SELECT

        order_id,

        DATE_DIFF(
            'day',
            CAST(order_purchase_timestamp AS TIMESTAMP),
            CAST(order_delivered_customer_date AS TIMESTAMP)
        ) AS delivery_days,

        DATE_DIFF(
            'day',
            CAST(order_estimated_delivery_date AS TIMESTAMP),
            CAST(order_delivered_customer_date AS TIMESTAMP)
        ) AS days_vs_estimate

    FROM orders

    WHERE order_delivered_customer_date IS NOT NULL

)

SELECT

    COUNT(*) AS delivered_orders,

    ROUND(
        AVG(delivery_days),
        2
    ) AS average_delivery_days,

    COUNT(
        CASE
            WHEN days_vs_estimate <= 0 THEN 1
        END
    ) AS on_time_orders,

    COUNT(
        CASE
            WHEN days_vs_estimate > 0 THEN 1
        END
    ) AS late_orders,

    ROUND(

        100.0 *
        COUNT(
            CASE
                WHEN days_vs_estimate > 0 THEN 1
            END
        )
        / COUNT(*),

        2

    ) AS late_delivery_rate_pct

FROM delivery_metrics;


-- ============================================================
-- 3. Delivery status vs review score
-- ============================================================

WITH delivery_status AS (

    SELECT

        o.order_id,

        CASE

            WHEN CAST(
                o.order_delivered_customer_date AS TIMESTAMP
            )
            <= CAST(
                o.order_estimated_delivery_date AS TIMESTAMP
            )

            THEN 'On Time'

            ELSE 'Late'

        END AS delivery_status

    FROM orders o

    WHERE
        o.order_delivered_customer_date IS NOT NULL

),

reviews AS (

    SELECT

        order_id,

        review_score

    FROM order_reviews

)

SELECT

    d.delivery_status,

    COUNT(*) AS reviewed_orders,

    ROUND(
        AVG(r.review_score),
        2
    ) AS average_review_score,

    ROUND(
        100.0 *
        AVG(
            CASE
                WHEN r.review_score <= 2
                THEN 1
                ELSE 0
            END
        ),
        2
    ) AS negative_review_rate_pct

FROM delivery_status d

JOIN reviews r
    ON d.order_id = r.order_id

GROUP BY d.delivery_status

ORDER BY d.delivery_status;


-- ============================================================
-- 4. Review score distribution
-- ============================================================

SELECT

    review_score,

    COUNT(*) AS reviews,

    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage_of_reviews

FROM order_reviews

GROUP BY review_score

ORDER BY review_score;
