from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

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
    
    # Handle PostgreSQL URL format (Koyeb, Aiven, etc.)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Create engine with connection pooling for production
    if "sqlite" in DATABASE_URL:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
    else:
        engine = create_engine(
            DATABASE_URL, 
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20,
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
