#!/usr/bin/env python3
"""
Setup script for PostgreSQL with pgvector extension.
This script helps create the necessary database and extension for the HR Assistant.
"""

import argparse
import os
import subprocess
import sys
import getpass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(command):
    """Run a shell command and print output"""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(f"Error: {stderr.decode('utf-8')}")
        return False
    
    print(f"Output: {stdout.decode('utf-8')}")
    return True

def check_postgresql_installation():
    """Check if PostgreSQL is installed"""
    try:
        # Try to run psql version command
        result = subprocess.run(
            ["psql", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"PostgreSQL is installed: {result.stdout.strip()}")
            return True
        else:
            print("PostgreSQL is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("PostgreSQL is not installed or not in PATH")
        return False

def create_database(dbname, username=None):
    """Create PostgreSQL database if it doesn't exist"""
    # Get current username in a reliable way
    current_user = getpass.getuser()
    
    # Check if database exists - use peer authentication instead of password
    check_db_cmd = f"psql -c \"SELECT 1 FROM pg_database WHERE datname = '{dbname}'\" -t postgres"
    result = subprocess.run(check_db_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if "1" in result.stdout.decode('utf-8').strip():
        print(f"Database '{dbname}' already exists")
        return True
    
    # Try to create database using peer authentication
    create_db_cmd = f"createdb {dbname}"
    if run_command(create_db_cmd):
        print(f"Database '{dbname}' created successfully")
        return True
    else:
        # Try with sudo as postgres user
        print("Attempting to create database as postgres user...")
        create_db_cmd = f"sudo -u postgres createdb {dbname}"
        if run_command(create_db_cmd):
            print(f"Database '{dbname}' created successfully by postgres user")
            print(f"Now granting permissions to the current user...")
            grant_cmd = f"sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE {dbname} TO {current_user}\""
            run_command(grant_cmd)
            return True
        else:
            print(f"Failed to create database '{dbname}'")
            print("Try running this command manually: sudo -u postgres createdb hr_assistant")
            return False

def create_pgvector_extension(dbname):
    """Create pgvector extension in the database"""
    # Check if the extension is available using peer authentication
    check_ext_cmd = f"psql -d {dbname} -c \"SELECT extname FROM pg_extension WHERE extname = 'vector'\" -t"
    result = subprocess.run(check_ext_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if 'vector' in result.stdout.decode('utf-8'):
        print("pgvector extension is already installed")
        return True
    
    # Try to install pgvector extension
    install_ext_cmd = f"psql -d {dbname} -c 'CREATE EXTENSION IF NOT EXISTS vector;'"
    if run_command(install_ext_cmd):
        print("pgvector extension installed successfully")
        return True
    else:
        # Try with sudo as postgres
        print("Attempting to install pgvector extension as postgres user...")
        install_ext_cmd = f"sudo -u postgres psql -d {dbname} -c 'CREATE EXTENSION IF NOT EXISTS vector;'"
        if run_command(install_ext_cmd):
            print("pgvector extension installed successfully by postgres user")
            return True
        else:
            print("Failed to install pgvector extension. Make sure it's installed in your system.")
            print("For Debian/Ubuntu: sudo apt-get install postgresql-server-dev-all")
            print("Then: sudo apt-get install postgresql-16-pgvector")  # Using the version you have (16.8)
            print("Or install from source: https://github.com/pgvector/pgvector#installation")
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Setup PostgreSQL with pgvector for HR Assistant')
    parser.add_argument('--dbname', default=os.getenv('POSTGRES_DBNAME', 'hr_assistant'), help='Database name')
    args = parser.parse_args()
    
    current_user = getpass.getuser()
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installation():
        print("Please install PostgreSQL before continuing")
        sys.exit(1)
    
    # Create database
    if not create_database(args.dbname):
        sys.exit(1)
    
    # Create pgvector extension
    if not create_pgvector_extension(args.dbname):
        print("pgvector extension could not be installed automatically")
        print("Please install it manually before continuing")
        sys.exit(1)
    
    # Success
    print("PostgreSQL setup with pgvector completed successfully!")
    print(f"Connection string: postgresql://{current_user}@localhost:5433/{args.dbname}")
    
    # Update the .env file with the correct connection string
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            env_contents = f.read()
        
        # Replace the connection string
        updated_contents = env_contents.replace(
            "POSTGRES_USER=$(whoami)", 
            f"POSTGRES_USER={current_user}"
        ).replace(
            "POSTGRES_CONNECTION_STRING=postgresql://$(whoami)@localhost:5432/hr_assistant",
            f"POSTGRES_CONNECTION_STRING=postgresql://{current_user}@localhost:5433/{args.dbname}"
        )
        
        with open(env_file, "w") as f:
            f.write(updated_contents)
        
        print(f"Updated .env file with correct connection string")

if __name__ == "__main__":
    main()
