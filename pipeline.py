import subprocess
import sys

def run_script(script_path):
    """Runs a Python script and stops the pipeline if it fails."""
    print(f"\n{'='*50}")
    print(f"🚀 RUNNING: {script_path}")
    print(f"{'='*50}")
    
    # Run the script using the current Python environment
    result = subprocess.run([sys.executable, script_path])
    
    # A return code of 0 means success. Anything else means it crashed.
    if result.returncode != 0:
        print(f"\n❌ PIPELINE HALTED: Error in {script_path}")
        sys.exit(1)
    else:
        print(f"\n✅ SUCCESS: {script_path} completed.")

if __name__ == "__main__":
    print("Starting NovaCart ELT Pipeline...")
    
    # Step 1: Extract
    run_script("src/extract/extract_postgres.py")
    run_script("src/extract/extract_csv.py")
    
    # Step 2: Validate
    run_script("src/validation/validate_logistics.py")
    
    # Step 3: Load
    run_script("src/load/load_warehouse.py")

    # Step 4: Transform
    run_script("src/transform/build_star_schema.py")

    # Step 5: Data Quality Checks
    run_script("src/quality/test_gold_schema.py")
    
    print("\n🎉 PIPELINE FINISHED SUCCESSFULLY! 🎉")