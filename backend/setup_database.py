#!/usr/bin/env python3
"""
Database Setup Guide for Agent Builder
Provides options for both PostgreSQL and SQLite setup
"""

import os
import sys
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def check_postgresql_installed():
    """Check if PostgreSQL is available"""
    import subprocess
    try:
        subprocess.run(['psql', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_sqlite_database():
    """Set up SQLite database as a simple alternative"""
    print("🗄️ Setting up SQLite Database (Simple Local Option)")
    print("=" * 60)
    
    # SQLite database path
    db_path = os.path.join(os.getcwd(), "agent_builder.db")
    
    try:
        # Create SQLite database
        conn = sqlite3.connect(db_path)
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        
        print(f"✅ SQLite database created successfully!")
        print(f"   Database path: {db_path}")
        print(f"   SQLite version: {version}")
        
        conn.close()
        
        # Update .env file for SQLite
        database_url = f"sqlite:///{db_path}"
        update_env_file_sqlite(database_url)
        
        return True
        
    except Exception as e:
        print(f"❌ SQLite setup failed: {e}")
        return False

def update_env_file_sqlite(database_url):
    """Update .env file with SQLite configuration"""
    print("\n📝 Updating .env file for SQLite...")
    
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
    
    print(f"✅ Updated .env file with SQLite database URL")
    return True

def test_sqlite_with_sqlalchemy():
    """Test SQLite database with SQLAlchemy"""
    print("\n🧪 Testing SQLite with SQLAlchemy...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Reload environment to get updated DATABASE_URL
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            print("❌ DATABASE_URL not found")
            return False
        
        print(f"🔗 Database URL: {database_url}")
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT sqlite_version()"))
            version = result.fetchone()[0]
            print(f"✅ SQLAlchemy + SQLite connection successful!")
            print(f"   SQLite version: {version}")
        
        return True
        
    except ImportError:
        print("❌ SQLAlchemy not installed")
        print("   Install with: pip install sqlalchemy")
        return False
    except Exception as e:
        print(f"❌ SQLAlchemy test failed: {e}")
        return False

def show_postgresql_installation_guide():
    """Show detailed PostgreSQL installation guide"""
    print("\n" + "=" * 80)
    print("📦 PostgreSQL Installation Guide")
    print("=" * 80)
    
    print("\n🪟 Windows Installation:")
    print("1. Go to: https://www.postgresql.org/download/windows/")
    print("2. Download the PostgreSQL installer")
    print("3. Run the installer as administrator")
    print("4. During installation:")
    print("   - Choose installation directory (default is fine)")
    print("   - Select components (keep all selected)")
    print("   - Choose data directory (default is fine)")
    print("   - Set password for postgres user (remember this!)")
    print("   - Set port (default 5432 is fine)")
    print("   - Choose locale (default is fine)")
    print("5. After installation:")
    print("   - Add PostgreSQL bin directory to PATH")
    print("   - Test with: psql --version")
    
    print("\n🔧 Quick Setup Commands (run after installation):")
    print("psql -U postgres")
    print("CREATE DATABASE agent_builder;")
    print("\\q")
    
    print("\n⚙️ Then update your .env file:")
    print("DATABASE_URL=postgresql://postgres:your_password@localhost:5432/agent_builder")

def main():
    print("🚀 Database Setup Options for Agent Builder")
    print("=" * 70)
    
    print("\nChoose your database setup:")
    print("1. 🐘 PostgreSQL (Recommended for production)")
    print("2. 📄 SQLite (Simple, good for development)")
    
    # Check if PostgreSQL is available
    if check_postgresql_installed():
        print("\n✅ PostgreSQL is installed and available!")
        print("💡 Run 'python setup_local_postgres.py' to configure PostgreSQL")
    else:
        print("\n⚠️ PostgreSQL is not installed")
        
        choice = input("\nChoose option (1 for PostgreSQL guide, 2 for SQLite setup): ").strip()
        
        if choice == "1":
            show_postgresql_installation_guide()
            print(f"\n📋 After installing PostgreSQL:")
            print("1. Restart your terminal/command prompt")
            print("2. Run: python setup_local_postgres.py")
            
        elif choice == "2":
            print("\n🔄 Setting up SQLite database...")
            
            if setup_sqlite_database():
                if test_sqlite_with_sqlalchemy():
                    print("\n" + "=" * 70)
                    print("🎉 SQLite Database Setup Complete!")
                    print("=" * 70)
                    print("✅ SQLite database created")
                    print("✅ .env file updated")
                    print("✅ SQLAlchemy connection tested")
                    
                    print("\n🚀 Next Steps:")
                    print("1. Your app will now use SQLite database")
                    print("2. Start your FastAPI server: python -m uvicorn app.main:app --reload")
                    print("3. Test your API endpoints")
                    
                    print("\n💡 Note: SQLite is perfect for development!")
                    print("   For production, consider setting up PostgreSQL later")
                else:
                    print("⚠️ SQLite setup completed but SQLAlchemy test failed")
            else:
                print("❌ SQLite setup failed")
        else:
            print("❌ Invalid choice")
            
        print(f"\n📊 Current .env configuration:")
        database_url = os.getenv("DATABASE_URL", "Not set")
        print(f"   DATABASE_URL={database_url}")

if __name__ == "__main__":
    main()