import os
import sqlite3

# Set the database URL environment variable
os.environ['DATABASE_URL'] = 'sqlite:///./app.db'

print("Starting forums table migration...")

try:
    # Connect to the database
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Check if the created_by column already exists
    cursor.execute("PRAGMA table_info(forums)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'created_by' not in column_names:
        print("Adding created_by column to forums table...")
        cursor.execute("ALTER TABLE forums ADD COLUMN created_by INTEGER REFERENCES users(id)")
        conn.commit()
        print("✅ created_by column added successfully!")
    else:
        print("✅ created_by column already exists!")
    
    # Verify the table structure
    cursor.execute("PRAGMA table_info(forums)")
    columns = cursor.fetchall()
    print("\nForums table structure:")
    for column in columns:
        print(f"  {column[1]} ({column[2]})")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error during migration: {e}")