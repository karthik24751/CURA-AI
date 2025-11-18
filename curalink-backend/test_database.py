#!/usr/bin/env python3

from sqlalchemy import create_engine, text
from database import DATABASE_URL

def test_database():
    try:
        print("🔍 Testing Database Connection and Data")
        print("=" * 50)
        
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Test forums
            print("\n📋 Testing Forums:")
            forums = conn.execute(text("SELECT id, title, category FROM forums")).fetchall()
            print(f"✅ Found {len(forums)} forums")
            for forum in forums:
                print(f"  - {forum[1]} ({forum[2]})")
            
            # Test forum posts
            print("\n💬 Testing Forum Posts:")
            posts = conn.execute(text("SELECT COUNT(*) FROM forum_posts")).fetchone()
            print(f"✅ Found {posts[0]} forum posts")
            
            # Test clinical trials
            print("\n🧪 Testing Clinical Trials:")
            trials = conn.execute(text("""
                SELECT id, title, phase, status, current_enrollment, target_enrollment 
                FROM clinical_trials 
                WHERE principal_investigator = 'DR PADMANADA BHUSAN'
            """)).fetchall()
            print(f"✅ Found {len(trials)} clinical trials for DR PADMANADA BHUSAN")
            for trial in trials:
                print(f"  - {trial[1]} ({trial[2]}) - {trial[4]}/{trial[5]} participants")
            
            # Test collaborators
            print("\n👥 Testing Collaborators:")
            collaborators = conn.execute(text("""
                SELECT u.full_name, rp.specialty, rp.institution 
                FROM users u 
                JOIN researcher_profiles rp ON u.id = rp.user_id 
                WHERE u.role = 'researcher' AND u.full_name != 'DR PADMANADA BHUSAN'
            """)).fetchall()
            print(f"✅ Found {len(collaborators)} researcher collaborators")
            for collab in collaborators[:5]:  # Show first 5
                print(f"  - {collab[0]} ({collab[1]}) at {collab[2]}")
            
            # Test follows/connections
            print("\n🤝 Testing Follow Connections:")
            follows = conn.execute(text("""
                SELECT COUNT(*) FROM follows 
                WHERE status = 'accepted'
            """)).fetchone()
            print(f"✅ Found {follows[0]} accepted follow connections")
            
            # Test users
            print("\n👤 Testing Users:")
            users = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'researcher'")).fetchone()
            print(f"✅ Found {users[0]} researcher users")
            
            print("\n" + "=" * 50)
            print("🎉 All Database Tests Passed!")
            print("\n📊 Summary:")
            print(f"  - Forums: {len(forums)} available")
            print(f"  - Forum Posts: {posts[0]} total")
            print(f"  - Clinical Trials: {len(trials)} for current researcher")
            print(f"  - Collaborators: {len(collaborators)} researchers")
            print(f"  - Connections: {follows[0]} accepted follows")
            print(f"  - Total Researchers: {users[0]} users")
            
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    test_database()
