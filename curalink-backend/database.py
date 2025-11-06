from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if running on Vercel (serverless) - fallback only
if os.getenv("VERCEL") and not DATABASE_URL:
    # Use SQLite for Vercel deployment as fallback
    DATABASE_URL = "sqlite:///./curalink.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
else:
    # Production or local development
    if not DATABASE_URL:
        # Fallback to local MySQL for development
        DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/curalink"

    # Ensure proper driver for MySQL URLs
    if DATABASE_URL.startswith("mysql://") and "pymysql" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

    # Handle PostgreSQL URL format (Koyeb, Aiven, etc.)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # For Vercel serverless, use minimal connection settings
    if os.getenv("VERCEL"):
        print(f"🔧 Vercel serverless mode detected")
        print(f"🔗 Database URL: {DATABASE_URL[:50]}...")
        try:
            # Try without SSL first for Vercel serverless
            engine = create_engine(
                DATABASE_URL.replace("?ssl-mode=REQUIRED", ""),  # Remove SSL requirement
                pool_pre_ping=False,
                pool_size=1,
                max_overflow=0,
                pool_recycle=60,
                connect_args={
                    'connect_timeout': 10,
                    'read_timeout': 10,
                },
                echo=False
            )
            print("✅ Database engine created successfully (without SSL)")
        except Exception as e:
            print(f"❌ Database connection error (without SSL): {e}")
            try:
                # Try with SSL if without SSL fails
                engine = create_engine(
                    DATABASE_URL,
                    pool_pre_ping=False,
                    pool_size=1,
                    max_overflow=0,
                    pool_recycle=60,
                    connect_args={
                        'ssl': {'ssl_mode': 'REQUIRED'},
                        'connect_timeout': 10,
                        'read_timeout': 10,
                    },
                    echo=False
                )
                print("✅ Database engine created successfully (with SSL)")
            except Exception as e2:
                print(f"❌ Database connection error (with SSL): {e2}")
                print("🔄 Falling back to SQLite...")
                DATABASE_URL = "sqlite:///./curalink.db"
                engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
    else:
        # Regular production connection (Render, Railway, etc.)
        connect_args = {}
        
        # Add SSL for PostgreSQL if needed
        if DATABASE_URL.startswith("postgresql://"):
            connect_args = {
                'connect_timeout': 10,
            }
        
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections every 5 minutes
            pool_size=3,  # Smaller pool for free tier
            max_overflow=5,
            connect_args=connect_args,
            echo=False
        )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
