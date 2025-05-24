#!/usr/bin/env python3
"""
Database reset utility - removes existing database files and recreates schema
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def reset_database():
    """Remove existing database files and recreate schema"""
    
    # Find and remove SQLite database files
    db_files = [
        backend_dir / "sql_app.db",
        backend_dir / "app.db",
        backend_dir / "freqtrade.db"
    ]
    
    for db_file in db_files:
        if db_file.exists():
            print(f"Removing {db_file}")
            db_file.unlink()
    
    # Import and recreate database schema
    try:
        from app.db.session import engine, init_db
        print("Recreating database schema...")
        init_db()
        print("✅ Database reset successfully!")
        
        # Test connection
        with engine.connect() as conn:
            print(f"✅ Database connection successful: {engine.url}")
            
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 Resetting database...")
    if reset_database():
        print("🎉 Database reset completed!")
    else:
        print("💥 Database reset failed!")
        sys.exit(1)