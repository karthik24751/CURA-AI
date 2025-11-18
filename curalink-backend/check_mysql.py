#!/usr/bin/env python3
"""
Script to check MySQL connection and database status
"""

import pymysql
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_mysql():
    """Check MySQL connection and database status"""
    
    print("🔍 Checking MySQL connection and database status...")
    
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
        
        print(f"🔗 Checking connection to MySQL server...")
        print(f"   Host: localhost")
        print(f"   User: {user}")
        print(f"   Database: {database_name}")
        
        # Connect to MySQL server (without specifying database first)
        connection = pymysql.connect(
            host='localhost',
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Connected to MySQL server successfully!")
        
        with connection.cursor() as cursor:
            # Check if database exists
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            
            db_exists = any(db['Database'] == database_name for db in databases)
            
            if db_exists:
                print(f"✅ Database '{database_name}' exists")
                
                # Switch to the database
                cursor.execute(f"USE {database_name}")
                
                # Check if forums table exists
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                forums_exists = any(table[f'Tables_in_{database_name}'] == 'forums' for table in tables)
                
                if forums_exists:
                    print("✅ Forums table exists")
                    
                    # Check columns in forums table
                    cursor.execute(f"DESCRIBE forums")
                    columns = cursor.fetchall()
                    
                    print("📋 Forums table columns:")
                    for column in columns:
                        print(f"   - {column['Field']} ({column['Type']})")
                        
                    # Check if created_by column exists
                    created_by_exists = any(column['Field'] == 'created_by' for column in columns)
                    
                    if created_by_exists:
                        print("✅ Column 'created_by' exists in forums table")
                    else:
                        print("⚠️  Column 'created_by' is missing from forums table")
                        print("💡 Run the migration script to add it:")
                        print("   python add_created_by_column.py")
                else:
                    print("❌ Forums table does not exist")
            else:
                print(f"❌ Database '{database_name}' does not exist")
                
        connection.close()
        
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        print("\n💡 Please check:")
        print("   - MySQL is running (sudo service mysql start)")
        print("   - Database credentials are correct")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = check_mysql()
    sys.exit(0 if success else 1)