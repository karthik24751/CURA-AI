#!/usr/bin/env python3
"""
Script to add the missing 'created_by' column to the forums table in MySQL database
"""

import pymysql
import sys
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def add_created_by_column():
    """Add the created_by column to the forums table"""
    
    print("🔧 Adding 'created_by' column to forums table...")
    
    try:
        # Get database connection details from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url or not database_url.startswith("mysql"):
            print("❌ This script only works with MySQL databases")
            return False
            
        # Parse the database URL
        # Format: mysql+pymysql://root:password@localhost:3306/database_name
        parts = database_url.split("://")[1].split("@")
        user_pass = parts[0].split(":")
        host_port_db = parts[1].split(":")
        host_port = host_port_db[0] + ":" + host_port_db[1].split("/")[0]
        database_name = host_port_db[1].split("/")[1]
        
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        
        # Connect to MySQL
        connection = pymysql.connect(
            host='localhost',
            user=user,
            password=password,
            database=database_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Check if the column already exists
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'forums' 
                AND COLUMN_NAME = 'created_by'
            """, (database_name,))
            
            result = cursor.fetchone()
            
            if result:
                print("✅ Column 'created_by' already exists in forums table")
                return True
            
            # Add the column
            cursor.execute("""
                ALTER TABLE forums 
                ADD COLUMN created_by INTEGER,
                ADD FOREIGN KEY (created_by) REFERENCES users(id)
            """)
            
            connection.commit()
            print("✅ Column 'created_by' added successfully to forums table!")
            
        connection.close()
        
        print("\n🎉 Migration complete!")
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        print("\n💡 Please check:")
        print("   - MySQL is running")
        print("   - Database credentials are correct")
        print("   - The 'curalink' database exists")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = add_created_by_column()
    sys.exit(0 if success else 1)