"""
Migration script: SQLite to PostgreSQL
Reads data from SQLite and inserts into PostgreSQL
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
from datetime import datetime
from app.config import settings


def migrate_table(sqlite_conn, pg_conn, table_name, columns_map=None):
    """
    Migrate a single table from SQLite to PostgreSQL
    
    Args:
        sqlite_conn: SQLite connection
        pg_conn: PostgreSQL connection
        table_name: Table name
        columns_map: Optional dict mapping SQLite column names to PostgreSQL
    """
    print(f"Migrating table: {table_name}")
    
    # Read from SQLite
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    column_names = [description[0] for description in sqlite_cursor.description]
    
    if not rows:
        print(f"  No data in {table_name}")
        return
    
    # Map columns if needed
    if columns_map:
        column_names = [columns_map.get(col, col) for col in column_names]
    
    # Insert into PostgreSQL
    pg_cursor = pg_conn.cursor()
    
    # Build INSERT statement
    placeholders = ', '.join(['%s'] * len(column_names))
    columns = ', '.join(column_names)
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
    
    # Convert rows to tuples
    values = [tuple(row) for row in rows]
    
    try:
        execute_values(pg_cursor, insert_sql, values)
        pg_conn.commit()
        print(f"  Migrated {len(rows)} rows")
    except Exception as e:
        pg_conn.rollback()
        print(f"  Error migrating {table_name}: {e}")
        raise


def main():
    """Main migration function"""
    # SQLite database path (adjust as needed)
    sqlite_path = os.getenv('SQLITE_DB_PATH', '/data/school_platform.db')
    
    if not os.path.exists(sqlite_path):
        print(f"SQLite database not found at: {sqlite_path}")
        return
    
    # Connect to SQLite
    print("Connecting to SQLite...")
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    
    # Connect to PostgreSQL
    print("Connecting to PostgreSQL...")
    pg_conn = psycopg2.connect(settings.DATABASE_URL)
    
    try:
        # List of tables to migrate (excluding device_bindings as per plan)
        tables = [
            'users',
            'videos',
            'posts',
            'comments',
            'rating_criteria',
            'dynamic_video_ratings',
            'video_likes',
            'suspensions',
            'star_bank',
            'messages',
            'telegram_settings'
        ]
        
        print(f"\nStarting migration at {datetime.now()}")
        print("=" * 50)
        
        for table in tables:
            try:
                migrate_table(sqlite_conn, pg_conn, table)
            except Exception as e:
                print(f"Failed to migrate {table}: {e}")
                continue
        
        print("=" * 50)
        print("Migration completed!")
        
        # Verify data integrity
        print("\nVerifying data integrity...")
        pg_cursor = pg_conn.cursor()
        
        for table in tables:
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = pg_cursor.fetchone()[0]
            
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            if pg_count == sqlite_count:
                print(f"  {table}: ✓ {pg_count} rows")
            else:
                print(f"  {table}: ✗ SQLite={sqlite_count}, PostgreSQL={pg_count}")
    
    finally:
        sqlite_conn.close()
        pg_conn.close()
        print("\nConnections closed.")


if __name__ == "__main__":
    main()

