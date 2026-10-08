# 🛒 E-Commerce Intelligence Hub

## SQL • DuckDB • Python • Customer Analytics • Business Intelligence

An end-to-end e-commerce analytics project demonstrating how SQL and Python can transform relational transaction data into actionable customer, revenue, product, retention, and operational insights.

The project uses the Brazilian E-Commerce Public Dataset by Olist and combines multiple relational tables in DuckDB to perform business-focused analytics.

---

## 🎯 Project Objective

The goal of this project is to answer practical business questions across the e-commerce customer lifecycle:

- How is revenue changing over time?
- Which customers generate the most value?
- What percentage of customers make repeat purchases?
- Which product categories drive revenue?
- Which customers are Champions, Loyal, At Risk, or Lost?
- How well does the business retain customers?
- Does delivery performance relate to customer satisfaction?
- Which products and categories contribute most to overall revenue?

---

# 🏗️ Project Architecture

```text
                    OLIST CSV DATA
                          │
                          ▼
                 ┌─────────────────┐
                 │     DuckDB      │
                 │ Relational DB   │
                 └────────┬────────┘
                          │
                          ▼
                    SQL ANALYTICS
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   Customers          Products         Operations
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
                     Python Layer
                          │
                          ▼
                  Streamlit Dashboard
                          │
                          ▼
                    Business Insights




    The project uses multiple related e-commerce datasets.
                                             CUSTOMERS
                             │
                             │ customer_id
                             ▼
                           ORDERS
                         /    │     \
                        /     │      \
                       ▼      ▼       ▼
                 PAYMENTS  REVIEWS  ORDER_ITEMS
                                      │
                              ┌───────┴───────┐
                              ▼               ▼
                          PRODUCTS         SELLERS
                              │
                              ▼
                    CATEGORY TRANSLATION


ecommerce-intelligence-hub/
│
├── dashboard/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── sql/
│   ├── 01_data_quality.sql
│   ├── 02_revenue_analysis.sql
│   ├── 03_customer_analysis.sql
│   ├── 04_product_analysis.sql
│   ├── 05_rfm_segmentation.sql
│   ├── 06_cohort_retention.sql
│   ├── 07_delivery_analysis.sql
│   └── 08_advanced_analytics.sql
│
├── src/
│   ├── load_data.py
│   └── run_sql.py
│
├── tests/
│
├── .gitignore
├── README.md
└── requirements.txt


## 📊 Dashboard

The project includes an interactive Streamlit dashboard covering:

- Executive revenue KPIs
- Monthly revenue trends
- Customer segmentation
- Repeat customer analysis
- Product category performance
- Customer retention cohorts
- Delivery performance
- Customer satisfaction

### Dashboard Preview

![Executive Overview](dashboard/screenshots/executive_overview.png)

### Customer Intelligence

![Customer Intelligence](dashboard/screenshots/customer_intelligence.png)

### Product Intelligence

![Product Intelligence](dashboard/screenshots/product_intelligence.png)

### Retention Analysis

![Retention](dashboard/screenshots/retention.png)

### Operations

![Operations](dashboard/screenshots/operations.png)

## 🛠️ Technical Skills Demonstrated

### SQL
- Complex JOINs
- CTEs
- Aggregations
- CASE statements
- Window functions
- RANK / NTILE
- Date and time analysis
- Cohort analysis
- RFM segmentation
- Data-quality checks

### Python
- Pandas
- DuckDB
- Data processing
- Analytical pipelines

### Visualization
- Streamlit
- Plotly
- Interactive dashboards

### Analytics
- Customer segmentation
- Revenue analysis
- Product analytics
- Retention analysis
- Operational analytics
- Customer satisfaction analysis

## 💡 Business Questions Answered

The analysis investigates:

1. How does revenue change over time?
2. Which product categories generate the most revenue?
3. How many customers make repeat purchases?
4. Which customer segments generate the greatest value?
5. How does customer retention change after the first purchase?
6. How does delivery performance relate to customer satisfaction?
7. Which categories contribute most to overall sales?