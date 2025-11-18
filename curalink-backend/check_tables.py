import os
os.environ['DATABASE_URL'] = 'sqlite:///./app.db'

from database import engine, Base
import logging

# Enable logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

print("Creating tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
except Exception as e:
    print(f"Error creating tables: {e}")

# Check tables in database
import sqlite3
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print('Tables in database:')
    for table in tables:
        print(table[0])
        
        # Show table structure for forums
        if table[0] == 'forums':
            print('  Forums table structure:')
            cursor.execute("PRAGMA table_info(forums)")
            columns = cursor.fetchall()
            for column in columns:
                print(f"    {column[1]} ({column[2]})")
                
except Exception as e:
    print(f"Error checking tables: {e}")
finally:
    conn.close()