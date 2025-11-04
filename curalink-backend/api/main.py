from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import hashlib
import json
import os

# Initialize FastAPI app
app = FastAPI(
    title="CuraLink API",
    description="AI-Powered Healthcare Discovery Platform",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# In-memory storage (your data will persist during the session)
users_db = {}
profiles_db = {}
notifications_db = {}
trials_db = {}
publications_db = {}
experts_db = {}
meetings_db = {}
favorites_db = {}

# Pydantic Models (Your Original Schemas)
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class PatientProfileUpdate(BaseModel):
    medical_condition: Optional[str] = None
    location: Optional[str] = None
    age: Optional[int] = None
    additional_info: Optional[str] = None

class ResearcherProfileUpdate(BaseModel):
    specialty: Optional[str] = None
    research_interests: Optional[str] = None
    institution: Optional[str] = None
    orcid_id: Optional[str] = None

class MeetingRequestCreate(BaseModel):
    expert_id: int
    message: Optional[str] = None

class FavoriteCreate(BaseModel):
    item_type: str
    item_id: str
    item_data: str

# Authentication Helper
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return None
    token = credentials.credentials
    # Simple token validation (in production, use proper JWT)
    for email, user_data in users_db.items():
        if f"token-{user_data['id']}-{hash(email)}" == token:
            return user_data
    return None

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to CuraLink API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Authentication Endpoints (Your Original Auth System)
@app.post("/api/auth/register")
async def register(user_data: UserCreate):
    try:
        email = user_data.email
        if email in users_db:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_id = len(users_db) + 1
        hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
        
        user = {
            "id": user_id,
            "email": email,
            "hashed_password": hashed_password,
            "full_name": user_data.full_name,
            "role": user_data.role,
            "created_at": datetime.utcnow().isoformat()
        }
        
        users_db[email] = user
        
        # Create profile
        if user_data.role == "patient":
            profiles_db[f"patient_{user_id}"] = {
                "user_id": user_id,
                "medical_condition": "",
                "location": "",
                "age": None,
                "additional_info": ""
            }
        else:
            profiles_db[f"researcher_{user_id}"] = {
                "user_id": user_id,
                "specialty": "",
                "research_interests": "",
                "institution": "",
                "orcid_id": ""
            }
        
        token = f"token-{user_id}-{hash(email)}"
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "full_name": user_data.full_name,
                "role": user_data.role
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    try:
        email = credentials.email
        password = credentials.password
        
        if email not in users_db:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        user = users_db[email]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if user["hashed_password"] != hashed_password:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        token = f"token-{user['id']}-{hash(email)}"
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Profile Endpoints (Your Original User System)
@app.get("/api/users/patient-profile")
async def get_patient_profile(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    profile_key = f"patient_{current_user['id']}"
    profile = profiles_db.get(profile_key, {})
    
    return {
        "id": current_user["id"],
        "medical_condition": profile.get("medical_condition", ""),
        "location": profile.get("location", ""),
        "age": profile.get("age"),
        "additional_info": profile.get("additional_info", "")
    }

@app.put("/api/users/patient-profile")
async def update_patient_profile(profile_data: PatientProfileUpdate, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    profile_key = f"patient_{current_user['id']}"
    if profile_key not in profiles_db:
        profiles_db[profile_key] = {"user_id": current_user["id"]}
    
    # Update profile
    for field, value in profile_data.dict(exclude_unset=True).items():
        profiles_db[profile_key][field] = value
    
    return {"message": "Profile updated successfully"}

# Notifications Endpoints (Your Original Notification System)
@app.get("/api/notifications/")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    if not current_user:
        return {"data": []}
    
    user_notifications = [
        notif for notif in notifications_db.values() 
        if notif.get("user_id") == current_user["id"]
    ]
    
    return {"data": user_notifications}

@app.put("/api/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if notification_id in notifications_db:
        notifications_db[notification_id]["read"] = True
    
    return {"message": "Notification marked as read"}

# Trials Endpoints (Your Original Trials System)
@app.get("/api/trials/")
async def get_trials():
    # Sample trial data (in production, fetch from external API)
    sample_trials = [
        {
            "nct_id": "NCT12345678",
            "title": "Advanced Diabetes Treatment Study",
            "summary": "A comprehensive study on new diabetes treatment methods",
            "condition": "Diabetes Type 2",
            "location": "New York, NY",
            "phase": "Phase 3",
            "status": "Recruiting",
            "sponsor": "Medical Research Institute"
        },
        {
            "nct_id": "NCT87654321",
            "title": "Cancer Immunotherapy Trial",
            "summary": "Testing new immunotherapy approaches for cancer treatment",
            "condition": "Cancer",
            "location": "Boston, MA",
            "phase": "Phase 2",
            "status": "Active",
            "sponsor": "Cancer Research Center"
        }
    ]
    
    return {"data": sample_trials}

# Publications Endpoints (Your Original Publications System)
@app.get("/api/publications/")
async def get_publications():
    sample_publications = [
        {
            "id": "1",
            "title": "Breakthrough in Diabetes Research",
            "authors": "Dr. Smith, Dr. Johnson",
            "journal": "Nature Medicine",
            "year": 2024,
            "abstract": "Recent discoveries in diabetes treatment mechanisms..."
        },
        {
            "id": "2",
            "title": "AI in Healthcare Diagnostics",
            "authors": "Dr. Wilson, Dr. Brown",
            "journal": "Science",
            "year": 2024,
            "abstract": "Application of artificial intelligence in medical diagnostics..."
        }
    ]
    
    return {"data": sample_publications}

# Experts Endpoints (Your Original Experts System)
@app.get("/api/experts/")
async def get_experts():
    sample_experts = [
        {
            "id": 1,
            "full_name": "Dr. Sarah Johnson",
            "specialty": "Endocrinology",
            "institution": "Harvard Medical School",
            "verified": True,
            "research_interests": "Diabetes, Metabolism"
        },
        {
            "id": 2,
            "full_name": "Dr. Michael Chen",
            "specialty": "Oncology",
            "institution": "Stanford University",
            "verified": True,
            "research_interests": "Cancer Immunotherapy"
        }
    ]
    
    return {"data": sample_experts}

# Meetings Endpoints (Your Original Meeting System)
@app.get("/api/meetings/")
async def get_meetings(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_meetings = [
        meeting for meeting in meetings_db.values()
        if meeting.get("requester_id") == current_user["id"] or meeting.get("expert_id") == current_user["id"]
    ]
    
    return user_meetings

@app.post("/api/meetings/")
async def create_meeting_request(meeting_data: MeetingRequestCreate, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    meeting_id = len(meetings_db) + 1
    meeting = {
        "id": meeting_id,
        "requester_id": current_user["id"],
        "expert_id": meeting_data.expert_id,
        "message": meeting_data.message,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    meetings_db[meeting_id] = meeting
    
    # Create notification for expert
    notification_id = len(notifications_db) + 1
    notifications_db[notification_id] = {
        "id": notification_id,
        "user_id": meeting_data.expert_id,
        "type": "meeting_request",
        "title": "New Meeting Request",
        "message": f"{current_user['full_name']} has requested a meeting",
        "read": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return meeting

# Favorites Endpoints (Your Original Favorites System)
@app.get("/api/favorites/")
async def get_favorites(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_favorites = [
        fav for fav in favorites_db.values()
        if fav.get("user_id") == current_user["id"]
    ]
    
    return user_favorites

@app.post("/api/favorites/")
async def add_favorite(favorite_data: FavoriteCreate, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    favorite_id = len(favorites_db) + 1
    favorite = {
        "id": favorite_id,
        "user_id": current_user["id"],
        "item_type": favorite_data.item_type,
        "item_id": favorite_data.item_id,
        "item_data": favorite_data.item_data,
        "created_at": datetime.utcnow().isoformat()
    }
    
    favorites_db[favorite_id] = favorite
    
    return favorite

# Chat Endpoints (Your Original Chat System)
@app.post("/api/chat/ai-assistant")
async def chat_with_ai(query: dict, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_message = query.get("message", "")
    
    # Simple AI response (in production, integrate with your SambaNova API)
    ai_response = f"Thank you for your question about '{user_message}'. I'm here to help you with healthcare information and clinical trial recommendations."
    
    return {
        "response": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    }

# Export for Vercel
handler = app
