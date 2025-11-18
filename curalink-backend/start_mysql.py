#!/usr/bin/env python3
"""
Script to start MySQL server if it's not running
"""

import subprocess
import sys
import time

def start_mysql():
    """Start MySQL server"""
    
    print("🔍 Checking if MySQL is running...")
    
    try:
        # Check if MySQL is running
        result = subprocess.run(['mysqladmin', 'ping'], capture_output=True, text=True)
        
        if "mysqld is alive" in result.stdout:
            print("✅ MySQL is already running")
            return True
        else:
            print("⚠️  MySQL is not running, attempting to start it...")
            
            # Try to start MySQL using different methods
            start_commands = [
                ['sudo', 'service', 'mysql', 'start'],
                ['brew', 'services', 'start', 'mysql'],
                ['sudo', 'systemctl', 'start', 'mysql']
            ]
            
            for command in start_commands:
                try:
                    print(f"🔧 Trying: {' '.join(command)}")
                    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        print("✅ MySQL started successfully")
                        # Wait a moment for MySQL to fully start
                        time.sleep(5)
                        return True
                    else:
                        print(f"⚠️  Command failed: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    print("⚠️  Command timed out")
                except Exception as e:
                    print(f"⚠️  Command failed: {e}")
            
            print("❌ Failed to start MySQL with any method")
            print("\n💡 Please start MySQL manually:")
            print("   - On Ubuntu/Debian: sudo service mysql start")
            print("   - On macOS with Homebrew: brew services start mysql")
            print("   - On other systems: Check your MySQL installation documentation")
            return False
            
    except FileNotFoundError:
        print("❌ mysqladmin not found. Is MySQL installed?")
        print("\n💡 Please install MySQL:")
        print("   - On Ubuntu/Debian: sudo apt install mysql-server")
        print("   - On macOS: brew install mysql")
        print("   - On other systems: Download from https://dev.mysql.com/downloads/mysql/")
        return False
    except Exception as e:
        print(f"❌ Error checking MySQL status: {e}")
        return False

if __name__ == "__main__":
    success = start_mysql()
    sys.exit(0 if success else 1)