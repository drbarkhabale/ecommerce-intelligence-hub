import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# PAGE CONFIG
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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #777;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


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

st.sidebar.divider()

st.sidebar.caption(
    "Built by Barkha Bale"
)

st.sidebar.caption(
    "SQL • DuckDB • Python • Streamlit"
)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    st.markdown(
        '<div class="main-title">🛒 E-Commerce Intelligence Hub</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Business Intelligence & Customer Analytics</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # GLOBAL DATE RANGE
    # --------------------------------------------------------

    dates = run_query(
        """
        SELECT

            MIN(
                CAST(
                    order_purchase_timestamp
                    AS TIMESTAMP
                )
            ) AS min_date,

            MAX(
                CAST(
                    order_purchase_timestamp
                    AS TIMESTAMP
                )
            ) AS max_date

        FROM orders
        """
    )

    min_date = dates.iloc[0]["min_date"].date()
    max_date = dates.iloc[0]["max_date"].date()


    selected_dates = st.sidebar.date_input(
        "📅 Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )


    if len(selected_dates) == 2:

        start_date = selected_dates[0]
        end_date = selected_dates[1]

    else:

        start_date = min_date
        end_date = max_date


    # --------------------------------------------------------
    # KPI QUERY
    # --------------------------------------------------------

    kpis = run_query(
        f"""
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

        WHERE

            CAST(
                o.order_purchase_timestamp
                AS DATE
            )

            BETWEEN
                '{start_date}'
                AND
                '{end_date}'
        """
    )


    revenue = float(
        kpis.iloc[0]["revenue"] or 0
    )

    orders = int(
        kpis.iloc[0]["orders"] or 0
    )

    customers = int(
        kpis.iloc[0]["customers"] or 0
    )

    aov = (
        revenue / orders
        if orders > 0
        else 0
    )


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "💰 Revenue",
        f"€{revenue:,.0f}"
    )

    c2.metric(
        "🛍️ Orders",
        f"{orders:,}"
    )

    c3.metric(
        "👥 Customers",
        f"{customers:,}"
    )

    c4.metric(
        "🧾 Average Order Value",
        f"€{aov:,.2f}"
    )


    st.divider()


    # --------------------------------------------------------
    # MONTHLY REVENUE
    # --------------------------------------------------------

    monthly = run_query(
        f"""
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

            ON o.order_id =
               p.order_id

        WHERE

            CAST(
                o.order_purchase_timestamp
                AS DATE
            )

            BETWEEN
                '{start_date}'
                AND
                '{end_date}'

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
        xaxis_title="",
        yaxis_title="Revenue",
        hovermode="x unified"
    )


    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )


    # --------------------------------------------------------
    # REVENUE BY CATEGORY
    # --------------------------------------------------------

    category = run_query(
        f"""
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

        JOIN orders o

            ON oi.order_id =
               o.order_id

        JOIN products p

            ON oi.product_id =
               p.product_id

        LEFT JOIN product_category_translation t

            ON p.product_category_name =
               t.product_category_name

        WHERE

            CAST(
                o.order_purchase_timestamp
                AS DATE
            )

            BETWEEN
                '{start_date}'
                AND
                '{end_date}'

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
        yaxis_title=""
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
        Understand customer purchasing behaviour,
        repeat purchasing and customer value.
        """
    )


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

                ON o.customer_id =
                   c.customer_id

            GROUP BY
                c.customer_unique_id
        )


        SELECT

            COUNT(*) AS customers,

            AVG(orders) AS avg_orders,

            SUM(
                CASE
                    WHEN orders > 1
                    THEN 1
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
        repeat_customers
        /
        total_customers
        *
        100
        if total_customers > 0
        else 0
    )


    c1, c2, c3 = st.columns(3)


    c1.metric(
        "👥 Unique Customers",
        f"{total_customers:,}"
    )

    c2.metric(
        "🛍️ Avg Orders / Customer",
        f"{avg_orders:.2f}"
    )

    c3.metric(
        "🔁 Repeat Customer Rate",
        f"{repeat_rate:.1f}%"
    )


    st.divider()


    # --------------------------------------------------------
    # RFM
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

                ON o.customer_id =
                   c.customer_id


            JOIN order_payments p

                ON o.order_id =
                   p.order_id


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


                ELSE
                    'Hibernating / Lost'

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


    left, right = st.columns(2)


    fig_rfm = px.pie(
        rfm,
        names="customer_segment",
        values="customers",
        hole=0.45,
        title="Customer Segmentation"
    )


    left.plotly_chart(
        fig_rfm,
        use_container_width=True
    )


    fig_rfm_revenue = px.bar(
        rfm.sort_values("revenue"),
        x="revenue",
        y="customer_segment",
        orientation="h",
        title="Revenue by Customer Segment"
    )


    right.plotly_chart(
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
        Identify the categories and products contributing
        most to revenue and sales volume.
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
            ) AS revenue,


            AVG(
                oi.price
            ) AS average_price


        FROM order_items oi


        JOIN products p

            ON oi.product_id =
               p.product_id


        LEFT JOIN product_category_translation t

            ON p.product_category_name =
               t.product_category_name


        GROUP BY 1


        ORDER BY revenue DESC
        """
    )


    top_products = (
        products
        .head(15)
        .sort_values("revenue")
    )


    left, right = st.columns(2)


    fig_revenue = px.bar(
        top_products,
        x="revenue",
        y="category",
        orientation="h",
        title="Top Categories by Revenue"
    )


    left.plotly_chart(
        fig_revenue,
        use_container_width=True
    )


    fig_units = px.bar(
        top_products.sort_values(
            "units_sold"
        ),
        x="units_sold",
        y="category",
        orientation="h",
        title="Top Categories by Units Sold"
    )


    right.plotly_chart(
        fig_units,
        use_container_width=True
    )


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

                ON o.customer_id =
                   c.customer_id


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

                ON o.customer_id =
                   c.customer_id
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

                        WHEN
                            months_since_first_purchase = 0

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

                100.0
                *
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


    pivot = retention.pivot(
        index="cohort_month",
        columns="months_since_first_purchase",
        values="retention_rate"
    )


    pivot.index = pivot.index.strftime(
        "%Y-%m"
    )


    pivot.columns = [
        f"Month {int(c)}"
        for c in pivot.columns
    ]


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
        Explore the relationship between delivery performance
        and customer satisfaction.
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


    left, right = st.columns(2)


    fig_delivery = px.bar(
        delivery,
        x="delivery_status",
        y="orders",
        title="On-Time vs Late Orders"
    )


    left.plotly_chart(
        fig_delivery,
        use_container_width=True
    )


    fig_reviews = px.bar(
        delivery,
        x="delivery_status",
        y="average_review_score",
        title="Average Review Score"
    )


    right.plotly_chart(
        fig_reviews,
        use_container_width=True
    )


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
    "E-Commerce Intelligence Hub"
)

st.sidebar.caption(
    "SQL • DuckDB • Python • Streamlit"
)

st.sidebar.caption(
    "Built by Barkha Bale"
)