#!/usr/bin/env python3

from sqlalchemy import create_engine, text
from database import DATABASE_URL

def fix_collaborators():
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔧 Fixing collaborators data...")
            
            # First, let's see what users exist
            users = conn.execute(text("SELECT id, full_name, email FROM users")).fetchall()
            print(f"Current users: {len(users)}")
            for user in users:
                print(f"  - {user[1]} ({user[2]})")
            
            # Add Indian researchers directly with proper error handling
            indian_researchers = [
                ('devi.shetty@narayana.com', 'Dr. Devi Prasad Shetty', 'Cardiac Surgery', 'Narayana Health', 'Pediatric cardiac surgery, Affordable healthcare'),
                ('randeep.guleria@aiims.edu', 'Dr. Randeep Guleria', 'Pulmonology', 'AIIMS New Delhi', 'Respiratory medicine, COVID-19 research'),
                ('trehan@medanta.org', 'Dr. Naresh Trehan', 'Cardiovascular Surgery', 'Medanta - The Medicity', 'Minimally invasive cardiac surgery'),
                ('prathap.reddy@apollo.com', 'Dr. Prathap C. Reddy', 'Cardiology', 'Apollo Hospitals', 'Healthcare management, Preventive cardiology'),
                ('ashok.seth@fortis.in', 'Dr. Ashok Seth', 'Interventional Cardiology', 'Fortis Escorts Heart Institute', 'Coronary interventions, Complex angioplasty'),
            ]
            
            for email, name, specialty, institution, interests in indian_researchers:
                try:
                    # Insert user
                    result = conn.execute(text("""
                        INSERT INTO users (email, full_name, role, password_hash, is_verified)
                        VALUES (:email, :name, 'researcher', 'hashed_password', 1)
                        ON DUPLICATE KEY UPDATE full_name = :name
                    """), {"email": email, "name": name})
                    
                    # Get user ID
                    user_result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
                    user_row = user_result.fetchone()
                    if user_row:
                        user_id = user_row[0]
                        
                        # Insert researcher profile
                        conn.execute(text("""
                            INSERT INTO researcher_profiles 
                            (user_id, specialty, institution, research_interests, orcid_id, verified, available_for_meetings)
                            VALUES (:user_id, :specialty, :institution, :interests, :orcid, 1, 1)
                            ON DUPLICATE KEY UPDATE 
                            specialty = :specialty, 
                            institution = :institution, 
                            research_interests = :interests
                        """), {
                            "user_id": user_id,
                            "specialty": specialty,
                            "institution": institution,
                            "interests": interests,
                            "orcid": f"0000-000{user_id}-{1000 + user_id}-{2000 + user_id}"
                        })
                        
                        print(f"✅ Added: {name}")
                    
                except Exception as e:
                    print(f"⚠️ Error adding {name}: {e}")
            
            # Now add follow relationships
            current_user_result = conn.execute(text("SELECT id FROM users WHERE full_name LIKE '%PADMANADA%' LIMIT 1"))
            current_user = current_user_result.fetchone()
            
            if current_user:
                current_user_id = current_user[0]
                print(f"\n🤝 Adding follow relationships for user ID: {current_user_id}")
                
                # Get all other researcher IDs
                other_researchers = conn.execute(text("""
                    SELECT id FROM users 
                    WHERE role = 'researcher' AND id != :current_user_id
                """), {"current_user_id": current_user_id}).fetchall()
                
                for researcher in other_researchers:
                    try:
                        conn.execute(text("""
                            INSERT INTO follows (follower_id, followed_id, status, created_at)
                            VALUES (:follower, :followed, 'accepted', NOW())
                            ON DUPLICATE KEY UPDATE status = 'accepted'
                        """), {
                            "follower": current_user_id,
                            "followed": researcher[0]
                        })
                        print(f"✅ Added follow relationship with user {researcher[0]}")
                    except Exception as e:
                        print(f"⚠️ Error adding follow: {e}")
            
            conn.commit()
            
            # Verify results
            print("\n📊 Verification:")
            researchers = conn.execute(text("""
                SELECT u.full_name, rp.specialty, rp.institution 
                FROM users u 
                JOIN researcher_profiles rp ON u.id = rp.user_id 
                WHERE u.role = 'researcher'
            """)).fetchall()
            
            print(f"✅ Total researchers with profiles: {len(researchers)}")
            for researcher in researchers:
                print(f"  - {researcher[0]} ({researcher[1]}) at {researcher[2]}")
            
            follows = conn.execute(text("SELECT COUNT(*) FROM follows WHERE status = 'accepted'")).fetchone()
            print(f"✅ Total accepted follows: {follows[0]}")
            
            print("\n🎉 Collaborators fixed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_collaborators()
