#!/usr/bin/env python3
"""
Comprehensive database setup script for CuraLink
This script will:
1. Check if MySQL is running and start it if needed
2. Check database and table status
3. Add missing columns if needed
"""

import subprocess
import sys
import time
import pymysql
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

# Load environment variables
load_dotenv()

def check_mysql_running():
    """Check if MySQL is running by trying to connect directly"""
    print("🔍 Checking if MySQL is running...")
    
    try:
        # Get database connection details from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url or not database_url.startswith("mysql"):
            print("❌ This script only works with MySQL databases")
            return False
            
        # Parse the database URL
        db_params = parse_database_url(database_url)
        
        # Try to connect to MySQL
        connection = pymysql.connect(
            host=db_params['host'] or 'localhost',
            port=db_params['port'] or 3306,
            user=db_params['user'] or 'root',
            password=db_params['password'] or '',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5
        )
        
        connection.close()
        print("✅ MySQL is running and accessible")
        return True
        
    except Exception as e:
        print(f"❌ MySQL connection failed: {str(e)}")
        return False

def parse_database_url(database_url):
    """Parse database URL and return connection parameters"""
    # Format: mysql+pymysql://root:password@localhost:3306/database_name
    # Remove the mysql+pymysql:// prefix
    url_without_prefix = database_url.replace('mysql+pymysql://', '')
    
    # Split by @ to separate user:pass from host:port/database
    user_pass, host_port_db = url_without_prefix.split('@', 1)
    
    # Split user:pass
    if ':' in user_pass:
        user, password = user_pass.split(':', 1)
        # URL decode the password to handle special characters
        password = unquote(password)
    else:
        user = user_pass
        password = ''
    
    # Split host:port/database
    if ':' in host_port_db:
        host_port, database = host_port_db.split('/', 1)
        if ':' in host_port:
            host, port_str = host_port.split(':', 1)
            port = int(port_str)
        else:
            host = host_port
            port = 3306
    else:
        host = host_port_db
        port = 3306
        database = ''
    
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }

def check_and_fix_database():
    """Check database structure and fix issues"""
    print("🔍 Checking database structure...")
    
    try:
        # Get database connection details from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url or not database_url.startswith("mysql"):
            print("❌ This script only works with MySQL databases")
            return False
            
        # Parse the database URL
        db_params = parse_database_url(database_url)
        
        # Connect to MySQL
        connection = pymysql.connect(
            host=db_params['host'] or 'localhost',
            port=db_params['port'] or 3306,
            user=db_params['user'] or 'root',
            password=db_params['password'] or '',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Check if database exists
            cursor.execute("SHOW DATABASES LIKE 'curalink'")
            result = cursor.fetchone()
            
            if not result:
                print(" Creating database 'curalink'...")
                cursor.execute("CREATE DATABASE curalink")
                cursor.execute("USE curalink")
            else:
                print("✅ Database 'curalink' exists")
                cursor.execute("USE curalink")
                
            # Check if forums table exists
            cursor.execute("SHOW TABLES LIKE 'forums'")
            result = cursor.fetchone()
            
            if not result:
                print("⚠️  Forums table doesn't exist - it will be created by the application")
            else:
                print("✅ Forums table exists")
                
                # Check if created_by column exists
                cursor.execute("SHOW COLUMNS FROM forums LIKE 'created_by'")
                result = cursor.fetchone()
                
                if not result:
                    print(" Adding 'created_by' column to forums table...")
                    cursor.execute("ALTER TABLE forums ADD COLUMN created_by INT")
                    print("✅ Added 'created_by' column to forums table")
                else:
                    print("✅ 'created_by' column already exists in forums table")
                    
        connection.commit()
        connection.close()
        print("✅ Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Starting CuraLink Database Setup...")
    
    # Check if MySQL is running
    if not check_mysql_running():
        print("⚠️  MySQL is not running. Please start MySQL and try again.")
        return False
    
    # Check and fix database structure
    if not check_and_fix_database():
        print("❌ Database setup failed!")
        return False
    
    print("🎉 Database setup completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)