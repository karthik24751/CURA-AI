import os
os.environ['DATABASE_URL'] = 'sqlite:///./app.db'

from database import engine, Base
from models import Forum
import logging

# Enable logging to see what's happening
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

print("Creating tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
except Exception as e:
    print(f"Error creating tables: {e}")
    
# Check if forums table exists
import sqlite3
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='forums'")
    result = cursor.fetchone()
    if result:
        print("Forums table exists!")
        # Show table structure
        cursor.execute("PRAGMA table_info(forums)")
        columns = cursor.fetchall()
        print("Forums table structure:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
    else:
        print("Forums table does not exist!")
except Exception as e:
    print(f"Error checking table: {e}")
finally:
    conn.close()