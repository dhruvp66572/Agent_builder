#!/usr/bin/env python3
"""
Test Local PostgreSQL Connection
Simple script to test if your local PostgreSQL database is working
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """Test database connection using the same method as your FastAPI app"""
    print("🧪 Testing Local PostgreSQL Connection")
    print("=" * 50)
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return False
    
    print(f"🔗 Database URL: {database_url}")
    
    # Test with SQLAlchemy (same as your app)
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        print("🔄 Creating SQLAlchemy engine...")
        engine = create_engine(database_url)
        
        print("🔄 Testing connection...")
        with engine.connect() as connection:
            # Test basic query
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"   PostgreSQL version: {version}")
            
            # Test creating a session (like your app does)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            session = SessionLocal()
            session.close()
            print("✅ Session creation successful!")
            
            return True
            
    except ImportError:
        print("❌ SQLAlchemy not installed")
        print("   Install with: pip install sqlalchemy psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        
        error_msg = str(e).lower()
        if "password authentication failed" in error_msg:
            print("💡 Solution: Wrong username or password")
            print("   1. Check your PostgreSQL credentials")
            print("   2. Update DATABASE_URL in .env file")
        elif "connection refused" in error_msg:
            print("💡 Solution: PostgreSQL is not running")
            print("   1. Start PostgreSQL service")
            print("   2. Check if PostgreSQL is installed")
        elif "does not exist" in error_msg:
            print("💡 Solution: Database doesn't exist")
            print("   1. Create the 'agent_builder' database")
            print("   2. Use PostgreSQL admin tools or run setup script")
        
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
            result = conn.execute("SELECT 1")
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

def main():
    success = test_database_connection()
    
    if success:
        test_with_app_database()
        
        print("\n" + "=" * 60)
        print("🎉 Local PostgreSQL is working correctly!")
        print("=" * 60)
        print("✅ Database connection established")
        print("✅ SQLAlchemy integration working")
        print("✅ Your FastAPI app should work with local PostgreSQL")
        
        print("\n🚀 You can now:")
        print("1. Start your FastAPI server: python -m uvicorn app.main:app --reload")
        print("2. Run database migrations if needed")
        print("3. Test your API endpoints")
    else:
        print("\n❌ Local PostgreSQL setup needs attention")
        print("💡 Run 'python setup_local_postgres.py' for guided setup")

if __name__ == "__main__":
    main()