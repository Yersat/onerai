#!/usr/bin/env python
"""
Script to migrate data from SQLite to PostgreSQL for onerai and partners_onerai projects.
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define paths
BASE_DIR = Path(__file__).resolve().parent
MANAGE_PY = BASE_DIR / "manage.py"

# Define database settings
ONERAI_DB_SETTINGS = {
    "NAME": os.environ.get("ONERAI_DB_NAME", "onerai"),
    "USER": os.environ.get("ONERAI_DB_USER", "onerai_user"),
    "PASSWORD": os.environ.get("ONERAI_DB_PASSWORD", "onerai_password"),
    "HOST": os.environ.get("ONERAI_DB_HOST", "localhost"),
    "PORT": os.environ.get("ONERAI_DB_PORT", "5432"),
}

PARTNERS_ONERAI_DB_SETTINGS = {
    "NAME": os.environ.get("PARTNERS_ONERAI_DB_NAME", "partners_onerai"),
    "USER": os.environ.get("PARTNERS_ONERAI_DB_USER", "partners_onerai_user"),
    "PASSWORD": os.environ.get("PARTNERS_ONERAI_DB_PASSWORD", "partners_onerai_password"),
    "HOST": os.environ.get("PARTNERS_ONERAI_DB_HOST", "localhost"),
    "PORT": os.environ.get("PARTNERS_ONERAI_DB_PORT", "5432"),
}

def dump_sqlite_data(settings_module, output_file):
    """
    Dump data from SQLite database to a JSON file.
    """
    print(f"Dumping data from {settings_module} SQLite database...")

    # Set the DJANGO_SETTINGS_MODULE environment variable
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_module

    # Run the dumpdata command
    result = subprocess.run(
        [sys.executable, str(MANAGE_PY), "dumpdata", "--exclude", "contenttypes", "--exclude", "auth.permission", "--output", output_file],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error dumping data: {result.stderr}")
        return False

    print(f"Data dumped to {output_file}")
    return True

def load_postgres_data(settings_module, input_file):
    """
    Load data from a JSON file into PostgreSQL database.
    """
    print(f"Loading data into {settings_module} PostgreSQL database...")

    # Set the DJANGO_SETTINGS_MODULE environment variable
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_module

    # Run the migrate command to create the database schema
    migrate_result = subprocess.run(
        [sys.executable, str(MANAGE_PY), "migrate"],
        capture_output=True,
        text=True,
    )

    if migrate_result.returncode != 0:
        print(f"Error migrating database: {migrate_result.stderr}")
        return False

    # Run the loaddata command
    load_result = subprocess.run(
        [sys.executable, str(MANAGE_PY), "loaddata", input_file],
        capture_output=True,
        text=True,
    )

    if load_result.returncode != 0:
        print(f"Error loading data: {load_result.stderr}")
        return False

    print(f"Data loaded from {input_file}")
    return True

def migrate_project(settings_module, dump_file):
    """
    Migrate a project from SQLite to PostgreSQL.
    """
    print(f"\nMigrating {settings_module} project...")

    # Dump data from SQLite
    if not dump_sqlite_data(settings_module, dump_file):
        return False

    # Load data into PostgreSQL
    if not load_postgres_data(settings_module, dump_file):
        return False

    print(f"{settings_module} project migrated successfully!")
    return True

def main():
    """
    Main function to migrate both projects.
    """
    print("Starting migration from SQLite to PostgreSQL...\n")

    # Create dump files
    onerai_dump_file = BASE_DIR / "onerai_data.json"
    partners_onerai_dump_file = BASE_DIR / "partners_onerai_data.json"

    # Migrate onerai project
    migrate_project("onerai.settings", onerai_dump_file)

    # Migrate partners_onerai project
    migrate_project("partners_onerai.settings", partners_onerai_dump_file)

    print("\nMigration completed!")

if __name__ == "__main__":
    main()
