# CuraLink Database Setup Instructions

This document provides instructions for setting up the CuraLink database with the required schema changes.

## Prerequisites

1. MySQL server installed and running
2. Python 3.9+ installed
3. Required Python packages installed (`pip install -r requirements.txt`)

## Database Setup Steps

### 1. Check Current Database Status

First, check the current status of your MySQL database:

```bash
cd curalink-backend
python check_mysql.py
```

This script will:
- Verify MySQL is running
- Check if the `curalink` database exists
- Verify the `forums` table exists
- Check if the `created_by` column is present

### 2. Start MySQL (if needed)

If MySQL is not running, you can try to start it automatically:

```bash
python start_mysql.py
```

Or start it manually:
- **macOS (Homebrew)**: `brew services start mysql`
- **Ubuntu/Debian**: `sudo service mysql start`
- **Other Linux**: `sudo systemctl start mysql`

### 3. Add Missing Column

If the `created_by` column is missing from the `forums` table, add it:

```bash
python add_created_by_column.py
```

### 4. Run Complete Setup (Recommended)

For a complete automated setup, run:

```bash
python setup_database.py
```

This script will:
1. Check if MySQL is running
2. Start MySQL if needed
3. Verify database structure
4. Add missing columns if needed

## Manual Database Setup (Alternative)

If the automated scripts don't work, you can manually add the column:

1. Connect to MySQL:
   ```bash
   mysql -u root -p
   ```

2. Use the curalink database:
   ```sql
   USE curalink;
   ```

3. Add the missing column:
   ```sql
   ALTER TABLE forums ADD COLUMN created_by INTEGER, ADD FOREIGN KEY (created_by) REFERENCES users(id);
   ```

4. Verify the column was added:
   ```sql
   DESCRIBE forums;
   ```

## Starting the Application

After database setup is complete:

1. Start the backend server:
   ```bash
   cd curalink-backend
   python main.py
   ```

2. In another terminal, start the frontend:
   ```bash
   cd curalink-frontend
   npm run dev
   ```

## Troubleshooting

### MySQL Connection Issues

If you get connection errors:
1. Verify MySQL is running: `mysqladmin ping`
2. Check credentials in `.env` file
3. Ensure the `curalink` database exists

### Missing Database

If the `curalink` database doesn't exist:
```sql
CREATE DATABASE curalink CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Missing Tables

If tables are missing, the FastAPI application should create them automatically on first run.

## Need Help?

If you continue to have issues:
1. Check the console output for specific error messages
2. Verify all prerequisites are met
3. Ensure no other applications are using port 8000 (backend) or 3000 (frontend)