import os
import sys
import pandas as pd

# Ensure project root is in Python's search path when run by pipeline.py
sys.path.append(os.getcwd())
from src.load.load_warehouse import get_warehouse_connection


def run_quality_checks() -> None:
    """Runs post-transformation data quality tests against the Gold Star Schema."""
    engine = get_warehouse_connection()
    failures = []

    print("Running Gold Star Schema Data Quality Tests...")

    # TEST 1: Revenue Reconciliation (Bronze vs. Gold)
    bronze_rev = pd.read_sql(
        "SELECT COALESCE(SUM(total_amount), 0) AS total FROM bronze.orders;",
        engine,
    ).iloc[0]["total"]

    gold_rev = pd.read_sql(
        "SELECT COALESCE(SUM(total_amount), 0) AS total FROM gold.fact_orders;",
        engine,
    ).iloc[0]["total"]

    if round(float(bronze_rev), 2) != round(float(gold_rev), 2):
        failures.append(f"Revenue mismatch! Bronze=${bronze_rev} vs Gold=${gold_rev}")
    else:
        print(f"PASS [Test 1 - Revenue Parity]: Bronze (${bronze_rev}) == Gold (${gold_rev})")

    # TEST 2: Primary Key Uniqueness on gold.fact_orders (0 failing rows = PASS)
    duplicate_orders = pd.read_sql("""
        SELECT order_id, COUNT(*) AS count
        FROM gold.fact_orders
        GROUP BY order_id
        HAVING COUNT(*) > 1;
    """, engine)

    if not duplicate_orders.empty:
        failures.append(f"Duplicate order_ids found in gold.fact_orders:\n{duplicate_orders}")
    else:
        print("PASS [Test 2 - Unique Grain]: 0 duplicate order_ids in gold.fact_orders")

    # TEST 3: Referential Integrity (0 orphan user_ids = PASS)
    orphan_users = pd.read_sql("""
        SELECT f.order_id, f.user_id
        FROM gold.fact_orders f
        LEFT JOIN gold.dim_users u ON f.user_id = u.user_id
        WHERE u.user_id IS NULL;
    """, engine)

    if not orphan_users.empty:
        failures.append(f"Orphan user_ids found in gold.fact_orders:\n{orphan_users}")
    else:
        print("PASS [Test 3 - Referential Integrity]: All orders map to valid users in gold.dim_users")

    # Final Verdict: Fail fast if any test failed
    if failures:
        print("\nCRITICAL DATA QUALITY FAILURE:")
        for err in failures:
            print(f" - {err}")
        sys.exit(1)

    print("\nAll Gold Data Quality Tests PASSED!")


if __name__ == "__main__":
    run_quality_checks()