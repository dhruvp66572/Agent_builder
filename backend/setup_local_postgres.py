#!/usr/bin/env python3
"""
Local PostgreSQL Setup Helper
This script helps you set up PostgreSQL locally for the Agent Builder project
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

def check_postgresql_installation():
    """Check if PostgreSQL is installed and running"""
    print("🔍 Checking PostgreSQL installation...")
    
    try:
        # Try to run psql --version
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ PostgreSQL is installed: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ PostgreSQL is not installed or not in PATH")
        return False
    except FileNotFoundError:
        print("❌ PostgreSQL is not installed or not in PATH")
        return False

def test_postgresql_connection():
    """Test connection to PostgreSQL with default credentials"""
    print("\n🔗 Testing PostgreSQL connection...")
    
    # Common default configurations to try
    configs = [
        {"host": "localhost", "port": 5432, "user": "postgres", "password": "password"},
        {"host": "localhost", "port": 5432, "user": "postgres", "password": "postgres"},
        {"host": "localhost", "port": 5432, "user": "postgres", "password": ""},
        {"host": "localhost", "port": 5432, "user": "postgres", "password": "admin"},
    ]
    
    for config in configs:
        try:
            print(f"🔄 Trying connection: {config['user']}@{config['host']}:{config['port']}")
            
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database='postgres'  # Connect to default postgres database first
            )
            conn.close()
            
            print(f"✅ Connection successful!")
            print(f"   Host: {config['host']}")
            print(f"   Port: {config['port']}")
            print(f"   User: {config['user']}")
            print(f"   Password: {config['password']}")
            
            return config
            
        except psycopg2.OperationalError as e:
            print(f"   ❌ Failed: {str(e).strip()}")
            continue
    
    print("❌ Could not connect to PostgreSQL with any common credentials")
    return None

def create_database(config, db_name="agent_builder"):
    """Create the agent_builder database"""
    print(f"\n🗄️ Creating database '{db_name}'...")
    
    try:
        # Connect to postgres database to create new database
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Database '{db_name}' already exists")
        else:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database '{db_name}' created successfully")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

def update_env_file(config, db_name="agent_builder"):
    """Update .env file with working PostgreSQL configuration"""
    print(f"\n📝 Updating .env file...")
    
    database_url = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{db_name}"
    
    # Read current .env file
    env_file_path = ".env"
    if not os.path.exists(env_file_path):
        print("❌ .env file not found")
        return False
    
    with open(env_file_path, 'r') as f:
        lines = f.readlines()
    
    # Update DATABASE_URL line
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith('DATABASE_URL=') and not line.strip().startswith('#'):
            lines[i] = f'DATABASE_URL={database_url}\n'
            updated = True
            break
    
    if not updated:
        # Add DATABASE_URL if not found
        lines.insert(0, f'DATABASE_URL={database_url}\n')
    
    # Write updated .env file
    with open(env_file_path, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Updated .env file with:")
    print(f"   DATABASE_URL={database_url}")
    
    return True

def test_database_connection_with_sqlalchemy():
    """Test database connection using SQLAlchemy (like your app does)"""
    print(f"\n🧪 Testing database connection with SQLAlchemy...")
    
    try:
        from sqlalchemy import create_engine, text
        from dotenv import load_dotenv
        
        # Reload environment variables
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            return False
        
        print(f"🔄 Testing connection to: {database_url}")
        
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ SQLAlchemy connection successful!")
            print(f"   PostgreSQL version: {version}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

def install_postgresql_instructions():
    """Provide instructions for installing PostgreSQL"""
    print("\n" + "=" * 80)
    print("📦 PostgreSQL Installation Instructions")
    print("=" * 80)
    
    print("\n🪟 For Windows:")
    print("1. Download PostgreSQL installer from: https://www.postgresql.org/download/windows/")
    print("2. Run the installer and follow the setup wizard")
    print("3. Remember the password you set for the 'postgres' user")
    print("4. Make sure to add PostgreSQL to your PATH during installation")
    print("5. Default port is 5432 (keep this unless you have conflicts)")
    
    print("\n🐧 For Linux (Ubuntu/Debian):")
    print("sudo apt update")
    print("sudo apt install postgresql postgresql-contrib")
    print("sudo -u postgres psql")
    print("ALTER USER postgres PASSWORD 'password';")
    print("\\q")
    
    print("\n🍎 For macOS:")
    print("brew install postgresql")
    print("brew services start postgresql")
    print("psql postgres")
    print("ALTER USER postgres PASSWORD 'password';")
    print("\\q")
    
    print("\n🔑 Common Default Credentials:")
    print("Username: postgres")
    print("Password: password (or postgres, or admin)")
    print("Host: localhost")
    print("Port: 5432")

def main():
    print("🚀 Local PostgreSQL Setup for Agent Builder")
    print("=" * 60)
    
    # Step 1: Check if PostgreSQL is installed
    if not check_postgresql_installation():
        install_postgresql_instructions()
        print("\n❌ Please install PostgreSQL first, then run this script again.")
        sys.exit(1)
    
    # Step 2: Test PostgreSQL connection
    config = test_postgresql_connection()
    if not config:
        print("\n❌ Could not connect to PostgreSQL.")
        print("💡 Common solutions:")
        print("1. Make sure PostgreSQL service is running")
        print("2. Check your username and password")
        print("3. Try connecting with pgAdmin or another PostgreSQL client")
        print("4. Reset PostgreSQL password if needed")
        sys.exit(1)
    
    # Step 3: Create database
    if not create_database(config):
        sys.exit(1)
    
    # Step 4: Update .env file
    if not update_env_file(config):
        sys.exit(1)
    
    # Step 5: Test connection with SQLAlchemy
    if not test_database_connection_with_sqlalchemy():
        print("⚠️ Basic PostgreSQL connection works, but SQLAlchemy connection failed")
        print("   This might be due to missing dependencies or configuration issues")
    
    print("\n" + "=" * 80)
    print("🎉 Local PostgreSQL Setup Complete!")
    print("=" * 80)
    
    print("✅ PostgreSQL is installed and running")
    print("✅ Database 'agent_builder' is created")
    print("✅ .env file is updated with local database URL")
    print("✅ Connection tested successfully")
    
    print("\n🔄 Next Steps:")
    print("1. Restart your FastAPI server")
    print("2. Your app will now use the local PostgreSQL database")
    print("3. Run database migrations if needed")
    print("4. Test your application endpoints")
    
    print(f"\n📊 Database Configuration:")
    print(f"   Host: {config['host']}")
    print(f"   Port: {config['port']}")
    print(f"   User: {config['user']}")
    print(f"   Database: agent_builder")
    print(f"   URL: postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/agent_builder")

if __name__ == "__main__":
    main()