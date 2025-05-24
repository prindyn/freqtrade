#!/usr/bin/env python3
"""
Migration script to add authentication fields to the Bot model
Run this script to add auth_method, username, and password fields to existing bots table
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import DATABASE_URL

def run_migration():
    """Add authentication fields to bots table"""
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()
        
        try:
            print("Adding authentication fields to bots table...")
            
            # Add auth_method column
            connection.execute(text("""
                ALTER TABLE bots 
                ADD COLUMN IF NOT EXISTS auth_method VARCHAR DEFAULT 'token'
            """))
            
            # Add username column
            connection.execute(text("""
                ALTER TABLE bots 
                ADD COLUMN IF NOT EXISTS username VARCHAR
            """))
            
            # Add password column  
            connection.execute(text("""
                ALTER TABLE bots 
                ADD COLUMN IF NOT EXISTS password VARCHAR
            """))
            
            # Update existing bots to use token authentication
            connection.execute(text("""
                UPDATE bots 
                SET auth_method = 'token' 
                WHERE auth_method IS NULL
            """))
            
            # Commit transaction
            trans.commit()
            print("✅ Successfully added authentication fields to bots table")
            print("📋 Migration completed!")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    run_migration()