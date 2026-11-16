# NovaCart End-to-End ELT Data Pipeline

A production-style, containerized **Extract, Load, Transform (ELT)** data engineering pipeline built with **Python, PostgreSQL, Docker, Pandas, SQLAlchemy, and Pandera**. The pipeline ingests transactional e-commerce data and partner logistics feeds into a **Medallion Architecture (`bronze` / `gold`)** warehouse modeled as an analytics-ready **Star Schema**, protected by a **Dead Letter Queue (DLQ)** and automated post-transformation SQL data quality assertions.

---

## Architecture Overview

```text
+--------------------------+       +-------------------------------+
|  OLTP Source (Port 5432) |       |  Logistics Partner CSV Feed   |
|  novacart_production_db  |       |  data/raw/logistics.csv       |
|  (users, products,       |       +---------------+---------------+
|   orders)                |                       |
+------------+-------------+                       v
             |                         +-----------------------+
             | extract_postgres.py     | Pandera Data Contract |
             v                         | (lazy=True)           |
+--------------------------+           +-----------+-----------+
|  Parquet Staging         |                       |
|  data/raw/*.parquet      |            +----------+----------+
+------------+-------------+            |                     |
             |                          v (Valid)             v (Malformed)
             |             +------------------------+  +---------------------+
             |             | clean_logistics.parquet|  | Dead Letter Queue   |
             |             +------------+-----------+  | bad_logistics.csv   |
             |                          |              +---------------------+
             +-------------+------------+
                           | load_warehouse.py
                           v
+------------------------------------------------------------------+
|            Data Warehouse: novacart_data_warehouse (Port 5433)   |
|                                                                  |
|  [BRONZE SCHEMA]                    [GOLD SCHEMA - STAR SCHEMA]  |
|  - bronze.users         ----------> - gold.dim_users             |
|  - bronze.products      ----------> - gold.dim_products          |
|  - bronze.orders        ----+                                    |
|  - bronze.logistics     ----+-----> - gold.fact_orders           |
|                           (LEFT JOIN + COALESCE)                 |
+------------------------------------------------------------------+
                           |
                           v test_gold_schema.py
+------------------------------------------------------------------+
|  Automated Data Quality Gate (Fail-Fast Assertions)              |
|  1. Revenue Parity (Bronze SUM == Gold SUM)                      |
|  2. Primary Key Uniqueness (0 duplicate order_ids)               |
|  3. Referential Integrity (0 orphan user_ids)                    |
+------------------------------------------------------------------+