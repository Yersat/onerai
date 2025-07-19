#!/usr/bin/env python
"""
Script to collect static files for both onerai and partners_onerai projects.
"""
import os
import sys
import subprocess
from pathlib import Path

def collect_static_files(project_name, settings_module):
    """
    Collect static files for a project.
    """
    print(f"\nCollecting static files for {project_name}...")
    
    # Set the DJANGO_SETTINGS_MODULE environment variable
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_module
    
    # Determine the manage.py path
    if project_name == "partners_onerai":
        manage_py = Path("partners_onerai/manage.py")
        os.chdir("partners_onerai")
    else:
        manage_py = Path("manage.py")
    
    # Run the collectstatic command
    result = subprocess.run(
        [sys.executable, str(manage_py), "collectstatic", "--noinput"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        print(f"Error collecting static files: {result.stderr}")
        return False
    
    print(f"Static files for {project_name} collected successfully!")
    return True

def main():
    """
    Main function to collect static files for both projects.
    """
    print("Starting static files collection...\n")
    
    # Collect static files for onerai project
    collect_static_files("onerai", "onerai.settings_production")
    
    # Reset directory for partners_onerai
    os.chdir("..")
    
    # Collect static files for partners_onerai project
    collect_static_files("partners_onerai", "partners_onerai.settings_production")
    
    print("\nStatic files collection completed!")

if __name__ == "__main__":
    main()
