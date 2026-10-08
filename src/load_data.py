import duckdb
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "ecommerce.duckdb"

# Connect to DuckDB
con = duckdb.connect(str(DB_PATH))

print("Creating E-Commerce Intelligence database...")
print(f"Database: {DB_PATH}")
print()

# CSV files → database tables
tables = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}

for table_name, filename in tables.items():
    csv_path = DATA_DIR / filename

    print(f"Loading {table_name}...")

    con.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT *
        FROM read_csv_auto(
            '{csv_path}',
            header = true
        )
    """)

    count = con.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    ).fetchone()[0]

    print(f"  ✓ {table_name}: {count:,} rows")

print()
print("Database created successfully!")
print()

# Display all tables
print("Tables:")
result = con.execute("SHOW TABLES").fetchall()

for row in result:
    print(f"  ✓ {row[0]}")

con.close()
