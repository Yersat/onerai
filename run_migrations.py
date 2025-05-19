#!/usr/bin/env python
"""
Script to run migrations for onerai and partners_onerai projects.
"""
import os
import sys
import subprocess
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent
MANAGE_PY = BASE_DIR / "manage.py"

def run_migrations(settings_module):
    """
    Run migrations for a project.
    """
    print(f"\nRunning migrations for {settings_module}...")
    
    # Set the DJANGO_SETTINGS_MODULE environment variable
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_module
    
    # Run the migrate command
    result = subprocess.run(
        [sys.executable, str(MANAGE_PY), "migrate"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        print(f"Error running migrations: {result.stderr}")
        return False
    
    print(f"Migrations for {settings_module} completed successfully!")
    return True

def main():
    """
    Main function to run migrations for both projects.
    """
    print("Starting migrations...\n")
    
    # Run migrations for onerai project
    run_migrations("onerai.settings")
    
    # Run migrations for partners_onerai project
    run_migrations("partners_onerai.settings")
    
    print("\nAll migrations completed!")

if __name__ == "__main__":
    main()
