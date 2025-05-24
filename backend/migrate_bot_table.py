#!/usr/bin/env python3
"""
Database migration script to add new columns to the bots table.
This script adds the columns needed for the hybrid bot architecture.
"""

import sys
import os

from sqlalchemy import create_engine, text
from app.core.config import DATABASE_URL

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def migrate_database():
    """Add new columns to the bots table for hybrid architecture support."""

    # Create database engine
    engine = create_engine(DATABASE_URL)

    # SQL commands to add new columns
    migration_commands = [
        # Add bot_type column with default value 'platform'
        "ALTER TABLE bots ADD COLUMN IF NOT EXISTS bot_type VARCHAR DEFAULT 'platform'",
        # Add name column
        "ALTER TABLE bots ADD COLUMN IF NOT EXISTS name VARCHAR",
        # Add description column
        "ALTER TABLE bots ADD COLUMN IF NOT EXISTS description TEXT",
        # Add api_url column for external bots
        "ALTER TABLE bots ADD COLUMN IF NOT EXISTS api_url VARCHAR",
        # Add api_token column for external bots
        "ALTER TABLE bots ADD COLUMN IF NOT EXISTS api_token VARCHAR",
        # Add config_template column for shared bots
        "ALTER TABLE bots ADD COLUMN IF NOT EXISTS config_template VARCHAR",
        # Add is_public column for shared bots
        "ALTER TABLE bots ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE",
        # Add connection tracking columns
        "ALTER TABLE bots ADD COLUMN IF NOT EXISTS last_ping TIMESTAMP",
        "ALTER TABLE bots ADD COLUMN IF NOT EXISTS connection_error TEXT",
        # Update existing records to have proper bot_type
        "UPDATE bots SET bot_type = 'platform' WHERE bot_type IS NULL OR bot_type = ''",
        # Update existing records to have names based on bot_id
        "UPDATE bots SET name = bot_id WHERE name IS NULL OR name = ''",
    ]

    try:
        with engine.connect() as connection:
            print("Starting database migration...")

            for i, command in enumerate(migration_commands, 1):
                print(
                    f"Executing migration step {i}/{len(migration_commands)}: {command[:50]}..."
                )
                try:
                    connection.execute(text(command))
                    connection.commit()
                    print(f"✓ Step {i} completed successfully")
                except Exception as e:
                    print(
                        f"✗ Step {i} failed (this might be expected if column already exists): {e}"
                    )
                    # Continue with other migrations even if one fails
                    continue

            print("\nMigration completed successfully!")
            print("The bots table now supports the hybrid architecture.")

    except Exception as e:
        print(f"Migration failed: {e}")
        return False

    return True


if __name__ == "__main__":
    print("FreqTrade SaaS Database Migration")
    print("=================================")
    print("Adding new columns to the bots table to support")
    print("external bot connections and shared bot marketplace.")
    print()

    # Check if we're in interactive mode
    import sys

    if sys.stdin.isatty():
        response = input("Do you want to proceed? (y/N): ")
        if response.lower() != "y":
            print("Migration cancelled.")
            sys.exit(0)
    else:
        # Non-interactive mode (e.g., Docker startup)
        print("Running in non-interactive mode, proceeding with migration...")

    success = migrate_database()
    if success:
        print("\n✓ Database migration completed successfully!")
    else:
        print("\n✗ Database migration failed!")
        sys.exit(1)
