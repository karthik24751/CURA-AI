#!/usr/bin/env python3

from sqlalchemy import create_engine, text
from database import DATABASE_URL

def update_collaborators():
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔧 Updating collaborators with real Indian researchers...")
            
            # Add real Indian medical researchers (without deleting existing)
            indian_researchers = [
                {
                    'email': 'devi.shetty@narayana.com',
                    'name': 'Dr. Devi Prasad Shetty',
                    'specialty': 'Cardiac Surgery',
                    'institution': 'Narayana Health',
                    'interests': 'Pediatric cardiac surgery, Affordable healthcare, Heart transplantation'
                },
                {
                    'email': 'randeep.guleria@aiims.edu',
                    'name': 'Dr. Randeep Guleria',
                    'specialty': 'Pulmonology',
                    'institution': 'AIIMS New Delhi',
                    'interests': 'Respiratory medicine, COVID-19 research, Critical care'
                },
                {
                    'email': 'trehan@medanta.org',
                    'name': 'Dr. Naresh Trehan',
                    'specialty': 'Cardiovascular Surgery',
                    'institution': 'Medanta - The Medicity',
                    'interests': 'Minimally invasive cardiac surgery, Robotic surgery'
                },
                {
                    'email': 'prathap.reddy@apollo.com',
                    'name': 'Dr. Prathap C. Reddy',
                    'specialty': 'Cardiology',
                    'institution': 'Apollo Hospitals',
                    'interests': 'Healthcare management, Preventive cardiology, Telemedicine'
                },
                {
                    'email': 'ashok.seth@fortis.in',
                    'name': 'Dr. Ashok Seth',
                    'specialty': 'Interventional Cardiology',
                    'institution': 'Fortis Escorts Heart Institute',
                    'interests': 'Complex angioplasty, Coronary interventions, Structural heart disease'
                },
                {
                    'email': 'vivek.jawali@fortis.in',
                    'name': 'Dr. Vivek Jawali',
                    'specialty': 'Cardiac Surgery',
                    'institution': 'Fortis Hospitals Bangalore',
                    'interests': 'Heart transplantation, Mechanical circulatory support, ECMO'
                }
            ]
            
            added_users = []
            
            for researcher in indian_researchers:
                try:
                    # Insert user
                    conn.execute(text("""
                        INSERT INTO users (email, full_name, role, password_hash, is_verified, created_at)
                        VALUES (:email, :name, 'researcher', 'hashed_password', 1, NOW())
                        ON DUPLICATE KEY UPDATE 
                        full_name = :name, is_verified = 1
                    """), {"email": researcher['email'], "name": researcher['name']})
                    
                    # Get user ID
                    user_result = conn.execute(text("SELECT id FROM users WHERE email = :email"), 
                                             {"email": researcher['email']})
                    user_row = user_result.fetchone()
                    
                    if user_row:
                        user_id = user_row[0]
                        added_users.append(user_id)
                        
                        # Insert/update researcher profile
                        conn.execute(text("""
                            INSERT INTO researcher_profiles 
                            (user_id, specialty, institution, research_interests, orcid_id, verified, available_for_meetings, created_at)
                            VALUES (:user_id, :specialty, :institution, :interests, :orcid, 1, 1, NOW())
                            ON DUPLICATE KEY UPDATE 
                            specialty = :specialty, 
                            institution = :institution, 
                            research_interests = :interests,
                            verified = 1,
                            available_for_meetings = 1
                        """), {
                            "user_id": user_id,
                            "specialty": researcher['specialty'],
                            "institution": researcher['institution'],
                            "interests": researcher['interests'],
                            "orcid": f"0000-000{user_id}-{1000 + user_id}-{2000 + user_id}"
                        })
                        
                        print(f"✅ Added: {researcher['name']} ({researcher['specialty']})")
                    
                except Exception as e:
                    print(f"⚠️ Error adding {researcher['name']}: {e}")
            
            # Update the "Test Researcher" to have proper data
            try:
                test_user_result = conn.execute(text("SELECT id FROM users WHERE full_name = 'Test Researcher'"))
                test_user = test_user_result.fetchone()
                if test_user:
                    test_user_id = test_user[0]
                    # Update to Dr. Kiran Mazumdar-Shaw
                    conn.execute(text("""
                        UPDATE users SET 
                        full_name = 'Dr. Kiran Mazumdar-Shaw',
                        email = 'kiran.mazumdar@biocon.com'
                        WHERE id = :user_id
                    """), {"user_id": test_user_id})
                    
                    conn.execute(text("""
                        UPDATE researcher_profiles SET 
                        specialty = 'Biotechnology',
                        institution = 'Biocon Limited',
                        research_interests = 'Biopharmaceuticals, Personalized medicine, Biosimilars',
                        verified = 1,
                        available_for_meetings = 1
                        WHERE user_id = :user_id
                    """), {"user_id": test_user_id})
                    
                    added_users.append(test_user_id)
                    print("✅ Updated Test Researcher to Dr. Kiran Mazumdar-Shaw")
            except Exception as e:
                print(f"⚠️ Error updating test researcher: {e}")
            
            # Add follow relationships for current user
            current_user_result = conn.execute(text("""
                SELECT id FROM users 
                WHERE full_name LIKE '%PADMANADA%' 
                ORDER BY created_at ASC 
                LIMIT 1
            """))
            current_user = current_user_result.fetchone()
            
            if current_user:
                current_user_id = current_user[0]
                print(f"\n🤝 Adding collaborations for user ID: {current_user_id}")
                
                for user_id in added_users:
                    if user_id != current_user_id:
                        try:
                            conn.execute(text("""
                                INSERT INTO follows (follower_id, followed_id, status, created_at)
                                VALUES (:follower, :followed, 'accepted', NOW())
                                ON DUPLICATE KEY UPDATE status = 'accepted'
                            """), {
                                "follower": current_user_id,
                                "followed": user_id
                            })
                            print(f"✅ Added collaboration with user {user_id}")
                        except Exception as e:
                            print(f"⚠️ Error adding collaboration: {e}")
            
            conn.commit()
            
            # Verify results
            print("\n📊 Verification:")
            researchers = conn.execute(text("""
                SELECT u.id, u.full_name, rp.specialty, rp.institution 
                FROM users u 
                JOIN researcher_profiles rp ON u.id = rp.user_id 
                WHERE u.role = 'researcher' AND u.full_name != 'DR PADMANADA BHUSAN'
                ORDER BY u.full_name
            """)).fetchall()
            
            print(f"✅ Total collaborator researchers: {len(researchers)}")
            for researcher in researchers:
                print(f"  - ID:{researcher[0]} {researcher[1]} ({researcher[2]}) at {researcher[3]}")
            
            follows = conn.execute(text("SELECT COUNT(*) FROM follows WHERE status = 'accepted'")).fetchone()
            print(f"✅ Total accepted collaborations: {follows[0]}")
            
            print("\n🎉 Real Indian researchers updated successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_collaborators()
