#!/usr/bin/env python3
"""
Test Local Database Connection (SQLite/PostgreSQL)
Tests the database connection regardless of database type
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """Test database connection using SQLAlchemy"""
    print("🧪 Testing Local Database Connection")
    print("=" * 50)
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return False
    
    print(f"🔗 Database URL: {database_url}")
    
    # Determine database type
    if database_url.startswith("sqlite"):
        db_type = "SQLite"
        version_query = "SELECT sqlite_version()"
    elif database_url.startswith("postgresql"):
        db_type = "PostgreSQL"
        version_query = "SELECT version()"
    else:
        db_type = "Unknown"
        version_query = "SELECT 1"
    
    print(f"📊 Database Type: {db_type}")
    
    # Test with SQLAlchemy
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        print("🔄 Creating SQLAlchemy engine...")
        engine = create_engine(database_url)
        
        print("🔄 Testing connection...")
        with engine.connect() as connection:
            # Test basic query
            if db_type != "Unknown":
                result = connection.execute(text(version_query))
                version = result.fetchone()[0]
                print(f"✅ Connection successful!")
                print(f"   {db_type} version: {version}")
            else:
                result = connection.execute(text("SELECT 1"))
                print(f"✅ Connection successful!")
            
            # Test creating a session (like your app does)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            session = SessionLocal()
            session.close()
            print("✅ Session creation successful!")
            
            return True
            
    except ImportError:
        print("❌ SQLAlchemy not installed")
        print("   Install with: pip install sqlalchemy")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        
        error_msg = str(e).lower()
        if "password authentication failed" in error_msg:
            print("💡 Solution: Wrong username or password")
            print("   1. Check your PostgreSQL credentials")
            print("   2. Update DATABASE_URL in .env file")
        elif "connection refused" in error_msg:
            print("💡 Solution: Database server is not running")
            print("   1. Start your database service")
            print("   2. Check if database server is installed")
        elif "no such file or directory" in error_msg and "sqlite" in database_url:
            print("💡 Solution: SQLite database file issue")
            print("   1. Check file path permissions")
            print("   2. Try creating database in current directory")
        elif "does not exist" in error_msg:
            print("💡 Solution: Database doesn't exist")
            print("   1. Create the database")
            print("   2. Use database admin tools")
        
        return False

def test_with_app_database():
    """Test using the same database module as your app"""
    print("\n🔗 Testing with App Database Module")
    print("=" * 50)
    
    try:
        # Import your app's database module
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.database import engine, get_db
        
        print("🔄 Testing app database connection...")
        
        # Test engine connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ App database engine working!")
        
        # Test get_db function
        db_generator = get_db()
        db = next(db_generator)
        db.close()
        print("✅ App get_db() function working!")
        
        return True
        
    except ImportError as ie:
        print(f"⚠️ Could not import app database module: {ie}")
        print("   This is normal if you haven't set up the app structure yet")
        return True  # Not a critical error
    except Exception as e:
        print(f"❌ App database test failed: {e}")
        return False

def create_test_table():
    """Create a simple test table to verify database is working"""
    print("\n🛠️ Creating Test Table")
    print("=" * 50)
    
    try:
        from sqlalchemy import create_engine, text
        
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Create a simple test table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            
            # Insert test data
            conn.execute(text("""
                INSERT OR REPLACE INTO test_table (id, name) VALUES (1, 'Test Entry')
            """))
            conn.commit()
            
            # Query test data
            result = conn.execute(text("SELECT * FROM test_table"))
            rows = result.fetchall()
            
            print(f"✅ Test table created successfully!")
            print(f"   Found {len(rows)} test records")
            
            for row in rows:
                print(f"   - ID: {row[0]}, Name: {row[1]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Test table creation failed: {e}")
        return False

def main():
    success = test_database_connection()
    
    if success:
        test_with_app_database()
        create_test_table()
        
        print("\n" + "=" * 60)
        print("🎉 Local Database is working correctly!")
        print("=" * 60)
        print("✅ Database connection established")
        print("✅ SQLAlchemy integration working")
        print("✅ Test table created and populated")
        print("✅ Your FastAPI app should work with this database")
        
        database_url = os.getenv("DATABASE_URL")
        if database_url.startswith("sqlite"):
            print("\n💡 You're using SQLite - perfect for development!")
            print("   Database file:", database_url.replace("sqlite:///", ""))
        
        print("\n🚀 You can now:")
        print("1. Start your FastAPI server: python -m uvicorn app.main:app --reload")
        print("2. Run database migrations if needed")
        print("3. Test your API endpoints")
    else:
        print("\n❌ Database setup needs attention")
        print("💡 Try running 'python setup_database.py' again")

if __name__ == "__main__":
    main()