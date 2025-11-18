#!/usr/bin/env python3
"""
Test script to verify Render PostgreSQL database connection locally
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_database_connection(database_url):
    """Test database connection and create tables"""
    try:
        print("🔍 Testing database connection...")
        print(f"Database URL: {database_url[:50]}...")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL!")
            print(f"📊 Version: {version}")
        
        # Import models and create tables
        print("\n🔨 Creating database tables...")
        from database import Base
        from models import User, PatientProfile, ResearcherProfile, MeetingRequest, Notification, ChatMessage, Forum, ForumPost, Favorite, ClinicalTrial
        
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # Test table creation
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            print(f"\n📋 Created {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
        
        print("\n✅ Database is ready for deployment!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Get database URL from environment or prompt
    database_url = os.getenv("DATABASE_URL") or input("Enter your Render External Database URL: ").strip()
    
    if not database_url:
        print("❌ No database URL provided!")
        exit(1)
    
    test_database_connection(database_url)
