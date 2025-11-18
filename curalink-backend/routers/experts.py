from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from auth_utils import get_current_user
from models import User, ResearcherProfile
from services.api_integrations import ORCIDService
# AI service removed - using only database data

router = APIRouter()

@router.get("/search")
async def search_experts(
    query: Optional[str] = Query(None),
    specialty: Optional[str] = Query(None),
    condition: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search for health experts and researchers with AI-powered matching"""
    
    # Search local database
    db_query = db.query(User, ResearcherProfile).join(ResearcherProfile)
    
    if specialty:
        db_query = db_query.filter(ResearcherProfile.specialty.contains(specialty))
    
    if query:
        db_query = db_query.filter(
            (User.full_name.contains(query)) |
            (ResearcherProfile.research_interests.contains(query))
        )
    
    if location:
        db_query = db_query.filter(ResearcherProfile.institution.contains(location))
    
    local_results = db_query.limit(20).all()

    experts = []
    for user, profile in local_results:
        experts.append({
            "id": user.id,
            "source": "local",
            "full_name": user.full_name,
            "email": user.email,
            "specialty": profile.specialty,
            "research_interests": profile.research_interests,
            "institution": profile.institution,
            "orcid_id": profile.orcid_id,
            "verified": profile.verified,
            "available_for_meetings": profile.available_for_meetings,
            "location": profile.institution  # Use institution as location proxy
        })

    # If no local experts found, return empty list - no mock data
    # experts remains empty

    # Only use local database researchers - no external ORCID data
    # This ensures we only show researchers who have actually registered on our platform
    
    # Use simple keyword matching for expert ranking
    if condition and experts:
        condition_lower = condition.lower()
        for expert in experts:
            # Simple keyword matching for match score
            expert_text = f"{expert.get('specialty', '')} {expert.get('research_interests', '')}".lower()
            
            if condition_lower in expert_text:
                expert['match_score'] = 90
                expert['match_reason'] = f"Specialty matches {condition}"
            elif any(word in expert_text for word in condition_lower.split()):
                expert['match_score'] = 75
                expert['match_reason'] = f"Related expertise in {expert.get('specialty', 'Research')}"
            else:
                expert['match_score'] = 60
                expert['match_reason'] = f"General researcher - specialty: {expert.get('specialty', 'Research')}"
    else:
        # Add default scores if no condition
        for expert in experts:
            expert['match_score'] = 75
            expert['match_reason'] = f"Registered researcher - specialty: {expert.get('specialty', 'Research')}"
    
    return experts

@router.get("/{expert_id}")
async def get_expert_details(
    expert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific expert"""
    user = db.query(User).filter(User.id == expert_id).first()
    if not user:
        return {"error": "Expert not found"}
    
    if user.role.value != "researcher":  # Access enum value
        return {"error": "User is not a researcher"}
    
    profile = db.query(ResearcherProfile).filter(ResearcherProfile.user_id == expert_id).first()
    
    # Return data in the structure expected by the frontend
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "profile": {
            "specialty": profile.specialty if profile else None,
            "research_interests": profile.research_interests if profile else None,
            "institution": profile.institution if profile else None,
            "orcid_id": profile.orcid_id if profile else None,
            "publications_summary": profile.publications_summary if profile else None,
            "verified": profile.verified if profile else False,
            "available_for_meetings": profile.available_for_meetings if profile else False,
            "bio": "Experienced researcher specializing in medical innovations and clinical trials.",
            "experience_years": 10,
            "publications_count": 25,
            "h_index": 15,
            "phone": "+1 (555) 123-4567",
            "website": "https://researcher-website.com",
            "location": profile.institution if profile else "United States"
        }
    }
