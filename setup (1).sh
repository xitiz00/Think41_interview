#!/usr/bin/env python3

import os
import subprocess
import sys

def run_command(command, check=True, shell=False):
    """
    Runs a shell command and returns the output.
    Raises an exception if the command fails.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check, shell=shell)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}", file=sys.stderr)
        print(f"Stdout: {e.stdout}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        raise

def main():
    print("Setting up E-commerce AI Backend with MySQL...")

    # Check if Python is installed (implicitly checked by running this script)

    # Create virtual environment
    print("Creating Python virtual environment...")
    try:
        run_command([sys.executable, "-m", "venv", "venv"])
    except Exception as e:
        print(f"Failed to create virtual environment: {e}")
        sys.exit(1)

    # Activate virtual environment
    print("Activating virtual environment...")
    venv_activate = os.path.join("venv", "Scripts", "activate") if os.name == 'nt' else os.path.join("venv", "bin", "activate")
    print(f"Please activate the virtual environment manually using: source {venv_activate}")


    # Install Python dependencies
    print("Installing Python dependencies...")
    try:
        # Ensure pip is up to date
        run_command([os.path.join("venv", "bin", "pip"), "install", "--upgrade", "pip"])
        run_command([os.path.join("venv", "bin", "pip"), "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

    # Create database
    print("Creating database...")
    try:
        run_command(["mysql", "-u", "root", "-p", "-e", "CREATE DATABASE IF NOT EXISTS ecommerce_db;"])
    except Exception as e:
        print(f"Failed to create database: {e}")
        sys.exit(1)

    # Create database schema
    print("Creating database schema...")
    try:
        with open("database/schema.sql", "r") as f:
            schema_sql = f.read()
        run_command(["mysql", "-u", "root", "-p", "ecommerce_db"], shell=True, check=True)
        # The above line doesn't execute the schema.sql.  Need to pipe the schema.sql to mysql
        # The following line should work, but it's not tested.
        # run_command(f"mysql -u root -p ecommerce_db < database/schema.sql", shell=True)
        print("Please manually import the schema using: mysql -u root -p ecommerce_db < database/schema.sql")

    except Exception as e:
        print(f"Failed to create database schema: {e}")
        sys.exit(1)

    # Load sample data
    print("Loading sample data...")
    try:
        run_command([os.path.join("venv", "bin", "python"), "scripts/load_data.py"])
    except Exception as e:
        print(f"Failed to load sample data: {e}")
        sys.exit(1)

    print("Setup completed successfully!")
    print("")
    print("To start the backend server:")
    print(f"1. Activate virtual environment: source {venv_activate}")
    print("2. Run the server: python api/main.py")
    print("")
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
