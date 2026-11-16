import os
import sys
from sqlalchemy import text

# Ensure project root is in Python's search path when run by pipeline.py
sys.path.append(os.getcwd())
from src.load.load_warehouse import get_warehouse_connection


def build_star_schema() -> None:
    """Transforms Bronze tables into an analytics-ready Gold Star Schema."""
    try:
        engine = get_warehouse_connection()
        with engine.begin() as conn:
            print("Creating 'gold' schema if not exists...")
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS gold;"))

            # 1. Build gold.dim_users
            print("Building gold.dim_users...")
            conn.execute(text("""
                DROP TABLE IF EXISTS gold.dim_users;
                CREATE TABLE gold.dim_users AS
                SELECT
                    user_id,
                    first_name || ' ' || last_name AS full_name,
                    email,
                    registration_date
                FROM bronze.users;
            """))

            # 2. Build gold.dim_products
            print("Building gold.dim_products...")
            conn.execute(text("""
                DROP TABLE IF EXISTS gold.dim_products;
                CREATE TABLE gold.dim_products AS
                SELECT
                    product_id,
                    product_name,
                    category,
                    price AS unit_price
                FROM bronze.products;
            """))

            # 3. Build gold.fact_orders
            print("Building gold.fact_orders...")
            conn.execute(text("""
                DROP TABLE IF EXISTS gold.fact_orders;
                CREATE TABLE gold.fact_orders AS
                SELECT
                    o.order_id,
                    o.user_id,
                    o.product_id,
                    o.order_date,
                    o.quantity,
                    o.total_amount,
                    COALESCE(l.shipping_status, 'Quarantined / Pending') AS shipping_status,
                    l.estimated_delivery
                FROM bronze.orders o
                LEFT JOIN bronze.logistics l
                    ON o.order_id = l.order_id;
            """))

        print("Success! Gold Star Schema tables built.")

    except Exception as e:
        print(f"CRITICAL ERROR building Gold Star Schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_star_schema()