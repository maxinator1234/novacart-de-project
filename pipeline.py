import logging
import os
import subprocess
import sys
import time

# Ensure logs directory exists before configuring FileHandler
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(os.path.join("logs", "pipeline.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)


def run_script(script_path: str) -> None:
    """Runs a pipeline stage, logs its duration, and halts immediately on failure."""
    logging.info(f"STARTING STAGE: {script_path}")
    start_time = time.perf_counter()

    result = subprocess.run([sys.executable, script_path])

    # 1. Calculate how many seconds this stage took
    elapsed = round(time.perf_counter() - start_time, 2)

    # 2. Check if the script succeeded (0) or failed (anything else)
    if result.returncode != 0:
        logging.error(
            f"PIPELINE HALTED: {script_path} failed with exit code {result.returncode} after {elapsed}s"
        )
        sys.exit(1)
    else:
        logging.info(f"SUCCESS: {script_path} completed in {elapsed}s")


if __name__ == "__main__":
    pipeline_start = time.perf_counter()
    logging.info("=== NovaCart ELT Pipeline Started ===")

    stages = [
        "src/extract/extract_postgres.py",
        "src/extract/extract_csv.py",
        "src/validation/validate_logistics.py",
        "src/load/load_warehouse.py",
        "src/transform/build_star_schema.py",
        "src/quality/test_gold_schema.py",
    ]

    # 3. Run each stage in order
    for stage in stages:
        run_script(stage)

    total_elapsed = round(time.perf_counter() - pipeline_start, 2)
    logging.info(f"=== NovaCart ELT Pipeline Finished Successfully in {total_elapsed}s ===")