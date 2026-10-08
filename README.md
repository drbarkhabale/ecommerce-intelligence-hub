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