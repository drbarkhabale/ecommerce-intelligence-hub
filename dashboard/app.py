import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="E-Commerce Intelligence Hub",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DATABASE
# ============================================================

DB_PATH = "data/ecommerce.duckdb"


@st.cache_resource
def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)


con = get_connection()


# ============================================================
# QUERY HELPER
# ============================================================

@st.cache_data
def run_query(query):
    return con.execute(query).fetchdf()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🛒 E-Commerce Hub")

st.sidebar.markdown(
    """
    **Business Intelligence Dashboard**

    SQL + DuckDB + Python + Streamlit
    """
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Overview",
        "Customer Intelligence",
        "Product Intelligence",
        "Retention",
        "Operations"
    ]
)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    st.title("🛒 E-Commerce Intelligence Hub")

    st.subheader("Executive Overview")

    st.markdown(
        """
        A business-focused analytics dashboard built with
        **SQL, DuckDB, Python and Streamlit**.
        """
    )

    # --------------------------------------------------------
    # KPI QUERY
    # IMPORTANT:
    # customer_unique_id = actual customer
    # customer_id = order-specific customer record
    # --------------------------------------------------------

    kpis = run_query(
        """
        SELECT

            SUM(p.payment_value) AS revenue,

            COUNT(
                DISTINCT o.order_id
            ) AS orders,

            COUNT(
                DISTINCT c.customer_unique_id
            ) AS customers

        FROM orders o

        JOIN order_payments p
            ON o.order_id = p.order_id

        JOIN customers c
            ON o.customer_id = c.customer_id
        """
    )

    revenue = float(kpis.iloc[0]["revenue"])
    orders = int(kpis.iloc[0]["orders"])
    customers = int(kpis.iloc[0]["customers"])

    aov = revenue / orders if orders else 0


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💰 Total Revenue",
        f"€{revenue:,.0f}"
    )

    col2.metric(
        "🛍️ Orders",
        f"{orders:,}"
    )

    col3.metric(
        "👥 Customers",
        f"{customers:,}"
    )

    col4.metric(
        "🧾 Average Order Value",
        f"€{aov:,.2f}"
    )

    st.divider()


    # --------------------------------------------------------
    # MONTHLY REVENUE
    # --------------------------------------------------------

    monthly = run_query(
        """
        SELECT

            DATE_TRUNC(
                'month',
                CAST(
                    o.order_purchase_timestamp
                    AS TIMESTAMP
                )
            ) AS month,

            SUM(
                p.payment_value
            ) AS revenue

        FROM orders o

        JOIN order_payments p
            ON o.order_id = p.order_id

        GROUP BY 1

        ORDER BY 1
        """
    )

    fig_revenue = px.line(
        monthly,
        x="month",
        y="revenue",
        markers=True,
        title="Monthly Revenue"
    )

    fig_revenue.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TOP PRODUCT CATEGORIES
    # --------------------------------------------------------

    category = run_query(
        """
        SELECT

            COALESCE(
                t.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category,

            SUM(
                oi.price
            ) AS revenue

        FROM order_items oi

        JOIN products p
            ON oi.product_id = p.product_id

        LEFT JOIN product_category_translation t
            ON p.product_category_name =
               t.product_category_name

        GROUP BY 1

        ORDER BY revenue DESC

        LIMIT 10
        """
    )

    fig_category = px.bar(
        category.sort_values("revenue"),
        x="revenue",
        y="category",
        orientation="h",
        title="Top 10 Product Categories by Revenue"
    )

    fig_category.update_layout(
        xaxis_title="Revenue",
        yaxis_title="Category"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ============================================================
# CUSTOMER INTELLIGENCE
# ============================================================

elif page == "Customer Intelligence":

    st.title("👥 Customer Intelligence")

    st.markdown(
        """
        Customer-level analysis covering purchasing behaviour,
        repeat purchases and RFM segmentation.
        """
    )


    # --------------------------------------------------------
    # CUSTOMER KPIs
    # --------------------------------------------------------

    customer_kpis = run_query(
        """
        WITH customer_orders AS (

            SELECT

                c.customer_unique_id,

                COUNT(
                    DISTINCT o.order_id
                ) AS orders

            FROM orders o

            JOIN customers c
                ON o.customer_id = c.customer_id

            GROUP BY
                c.customer_unique_id
        )

        SELECT

            COUNT(*) AS customers,

            AVG(orders) AS avg_orders,

            SUM(
                CASE
                    WHEN orders > 1 THEN 1
                    ELSE 0
                END
            ) AS repeat_customers

        FROM customer_orders
        """
    )

    total_customers = int(
        customer_kpis.iloc[0]["customers"]
    )

    avg_orders = float(
        customer_kpis.iloc[0]["avg_orders"]
    )

    repeat_customers = int(
        customer_kpis.iloc[0]["repeat_customers"]
    )

    repeat_rate = (
        repeat_customers / total_customers * 100
        if total_customers > 0
        else 0
    )


    # --------------------------------------------------------
    # CUSTOMER KPI CARDS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "👥 Unique Customers",
        f"{total_customers:,}"
    )

    c2.metric(
        "🛍️ Average Orders / Customer",
        f"{avg_orders:.2f}"
    )

    c3.metric(
        "🔁 Repeat Customer Rate",
        f"{repeat_rate:.1f}%"
    )

    st.divider()


    # --------------------------------------------------------
    # RFM SEGMENTATION
    # --------------------------------------------------------

    rfm = run_query(
        """
        WITH analysis_date AS (

            SELECT

                MAX(
                    CAST(
                        order_purchase_timestamp
                        AS TIMESTAMP
                    )
                ) AS max_purchase_date

            FROM orders
        ),


        customer_rfm AS (

            SELECT

                c.customer_unique_id,

                DATE_DIFF(
                    'day',

                    MAX(
                        CAST(
                            o.order_purchase_timestamp
                            AS TIMESTAMP
                        )
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


            JOIN customers c
                ON o.customer_id = c.customer_id


            JOIN order_payments p
                ON o.order_id = p.order_id


            CROSS JOIN analysis_date a


            GROUP BY

                c.customer_unique_id,

                a.max_purchase_date
        ),


        rfm_scores AS (

            SELECT

                *,

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
        )


        SELECT

            CASE

                WHEN
                    recency_score
                    +
                    frequency_score
                    +
                    monetary_score >= 13

                    THEN 'Champions'


                WHEN
                    recency_score
                    +
                    frequency_score
                    +
                    monetary_score >= 10

                    THEN 'Loyal Customers'


                WHEN
                    recency_score
                    +
                    frequency_score
                    +
                    monetary_score >= 8

                    THEN 'Potential Loyalists'


                WHEN
                    recency_score
                    +
                    frequency_score
                    +
                    monetary_score >= 6

                    THEN 'At Risk'


                ELSE 'Hibernating / Lost'

            END AS customer_segment,


            COUNT(*) AS customers,


            SUM(
                monetary_value
            ) AS revenue


        FROM rfm_scores


        GROUP BY 1


        ORDER BY revenue DESC
        """
    )


    # --------------------------------------------------------
    # RFM CHART
    # --------------------------------------------------------

    fig_rfm = px.bar(
        rfm.sort_values("customers"),
        x="customers",
        y="customer_segment",
        orientation="h",
        title="Customer Segments"
    )

    fig_rfm.update_layout(
        xaxis_title="Number of Customers",
        yaxis_title="Segment"
    )

    st.plotly_chart(
        fig_rfm,
        use_container_width=True
    )


    # --------------------------------------------------------
    # RFM REVENUE
    # --------------------------------------------------------

    fig_rfm_revenue = px.bar(
        rfm.sort_values("revenue"),
        x="revenue",
        y="customer_segment",
        orientation="h",
        title="Revenue by Customer Segment"
    )

    fig_rfm_revenue.update_layout(
        xaxis_title="Revenue",
        yaxis_title="Segment"
    )

    st.plotly_chart(
        fig_rfm_revenue,
        use_container_width=True
    )


    st.subheader("Customer Segment Details")

    st.dataframe(
        rfm,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PRODUCT INTELLIGENCE
# ============================================================

elif page == "Product Intelligence":

    st.title("📦 Product Intelligence")

    st.markdown(
        """
        Product and category performance analysis covering
        orders, units sold and revenue.
        """
    )


    products = run_query(
        """
        SELECT

            COALESCE(
                t.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category,


            COUNT(
                DISTINCT oi.order_id
            ) AS orders,


            COUNT(*) AS units_sold,


            SUM(
                oi.price
            ) AS revenue


        FROM order_items oi


        JOIN products p
            ON oi.product_id = p.product_id


        LEFT JOIN product_category_translation t
            ON p.product_category_name =
               t.product_category_name


        GROUP BY 1


        ORDER BY revenue DESC
        """
    )


    # --------------------------------------------------------
    # TOP 15 CATEGORIES
    # --------------------------------------------------------

    top_products = products.head(15).sort_values(
        "revenue"
    )


    fig_products = px.bar(
        top_products,
        x="revenue",
        y="category",
        orientation="h",
        title="Top 15 Product Categories by Revenue"
    )

    fig_products.update_layout(
        xaxis_title="Revenue",
        yaxis_title="Category"
    )

    st.plotly_chart(
        fig_products,
        use_container_width=True
    )


    # --------------------------------------------------------
    # UNITS SOLD
    # --------------------------------------------------------

    top_units = products.head(15).sort_values(
        "units_sold"
    )


    fig_units = px.bar(
        top_units,
        x="units_sold",
        y="category",
        orientation="h",
        title="Top Product Categories by Units Sold"
    )

    fig_units.update_layout(
        xaxis_title="Units Sold",
        yaxis_title="Category"
    )

    st.plotly_chart(
        fig_units,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    st.subheader("Category Performance")

    st.dataframe(
        products,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# RETENTION
# ============================================================

elif page == "Retention":

    st.title("🔄 Customer Retention")

    st.markdown(
        """
        Cohort analysis showing how customer activity changes
        after the first purchase.
        """
    )


    retention = run_query(
        """
        WITH customer_first_purchase AS (

            SELECT

                c.customer_unique_id,

                DATE_TRUNC(
                    'month',

                    MIN(
                        CAST(
                            o.order_purchase_timestamp
                            AS TIMESTAMP
                        )
                    )
                ) AS cohort_month

            FROM orders o

            JOIN customers c
                ON o.customer_id = c.customer_id

            GROUP BY
                c.customer_unique_id
        ),


        customer_activity AS (

            SELECT DISTINCT

                c.customer_unique_id,

                DATE_TRUNC(
                    'month',

                    CAST(
                        o.order_purchase_timestamp
                        AS TIMESTAMP
                    )
                ) AS purchase_month

            FROM orders o

            JOIN customers c
                ON o.customer_id = c.customer_id
        ),


        cohort_activity AS (

            SELECT

                f.cohort_month,

                a.purchase_month,


                DATE_DIFF(
                    'month',

                    f.cohort_month,

                    a.purchase_month

                ) AS months_since_first_purchase,


                a.customer_unique_id


            FROM customer_first_purchase f


            JOIN customer_activity a

                ON f.customer_unique_id =
                   a.customer_unique_id
        ),


        cohort_counts AS (

            SELECT

                cohort_month,

                months_since_first_purchase,


                COUNT(
                    DISTINCT customer_unique_id
                ) AS active_customers


            FROM cohort_activity


            GROUP BY

                1,

                2
        ),


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


        SELECT

            c.cohort_month,

            c.months_since_first_purchase,


            ROUND(

                100.0 *
                c.active_customers
                /
                NULLIF(
                    s.cohort_size,
                    0
                ),

                2

            ) AS retention_rate


        FROM cohort_counts c


        JOIN cohort_sizes s

            ON c.cohort_month =
               s.cohort_month


        ORDER BY

            1,

            2
        """
    )


    # --------------------------------------------------------
    # RETENTION PIVOT
    # --------------------------------------------------------

    pivot = retention.pivot(
        index="cohort_month",
        columns="months_since_first_purchase",
        values="retention_rate"
    )


    pivot.index = pivot.index.strftime(
        "%Y-%m"
    )


    pivot.columns = [
        f"Month {int(column)}"
        for column in pivot.columns
    ]


    # --------------------------------------------------------
    # HEATMAP
    # --------------------------------------------------------

    fig_retention = px.imshow(
        pivot,
        aspect="auto",
        title="Customer Cohort Retention (%)",
        labels={
            "x": "Months Since First Purchase",
            "y": "Cohort",
            "color": "Retention %"
        }
    )


    st.plotly_chart(
        fig_retention,
        use_container_width=True
    )


    st.subheader("Retention Table")


    st.dataframe(
        pivot,
        use_container_width=True
    )


# ============================================================
# OPERATIONS
# ============================================================

elif page == "Operations":

    st.title("🚚 Operations & Customer Satisfaction")

    st.markdown(
        """
        Delivery performance and customer satisfaction analysis.
        """
    )


    delivery = run_query(
        """
        WITH delivery_status AS (

            SELECT

                o.order_id,


                CASE

                    WHEN

                        CAST(
                            o.order_delivered_customer_date
                            AS TIMESTAMP
                        )

                        <=

                        CAST(
                            o.order_estimated_delivery_date
                            AS TIMESTAMP
                        )

                    THEN 'On Time'


                    ELSE 'Late'

                END AS delivery_status


            FROM orders o


            WHERE

                o.order_delivered_customer_date
                IS NOT NULL


                AND

                o.order_estimated_delivery_date
                IS NOT NULL
        )


        SELECT

            d.delivery_status,


            COUNT(
                DISTINCT d.order_id
            ) AS orders,


            ROUND(
                AVG(r.review_score),
                2
            ) AS average_review_score


        FROM delivery_status d


        JOIN order_reviews r

            ON d.order_id =
               r.order_id


        GROUP BY

            d.delivery_status


        ORDER BY

            d.delivery_status
        """
    )


    # --------------------------------------------------------
    # DELIVERY CHART
    # --------------------------------------------------------

    c1, c2 = st.columns(2)


    fig_delivery = px.bar(
        delivery,
        x="delivery_status",
        y="orders",
        title="On-Time vs Late Orders"
    )


    fig_delivery.update_layout(
        xaxis_title="Delivery Status",
        yaxis_title="Orders"
    )


    c1.plotly_chart(
        fig_delivery,
        use_container_width=True
    )


    # --------------------------------------------------------
    # REVIEW CHART
    # --------------------------------------------------------

    fig_reviews = px.bar(
        delivery,
        x="delivery_status",
        y="average_review_score",
        title="Average Review Score"
    )


    fig_reviews.update_layout(
        xaxis_title="Delivery Status",
        yaxis_title="Average Review Score"
    )


    c2.plotly_chart(
        fig_reviews,
        use_container_width=True
    )


    # --------------------------------------------------------
    # OPERATIONS TABLE
    # --------------------------------------------------------

    st.subheader("Delivery Performance")


    st.dataframe(
        delivery,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "Built by Barkha Bale | "
    "SQL • DuckDB • Python • Streamlit"
)