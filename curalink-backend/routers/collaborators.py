from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from auth_utils import get_current_user
from models import User, ResearcherProfile, Follow
from services.api_integrations import ORCIDService

router = APIRouter()

@router.get("/my-collaborators")
async def get_my_collaborators(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get researchers that the current user is following (accepted connections)"""
    if current_user.role.value != "researcher":
        return {"collaborators": [], "count": 0}
    
    # Get accepted follows where current user is the follower
    follows = db.query(Follow, User, ResearcherProfile).join(
        User, Follow.followed_id == User.id
    ).outerjoin(
        ResearcherProfile, ResearcherProfile.user_id == User.id
    ).filter(
        Follow.follower_id == current_user.id,
        Follow.status == "accepted"
    ).all()
    
    collaborators = []
    for follow, user, profile in follows:
        if profile:
            collaborators.append({
                "id": user.id,
                "name": user.full_name,
                "specialty": profile.specialty or "Research",
                "institution": profile.institution or "Not specified",
                "projects": 0,  # TODO: Count actual projects
                "status": "active",
                "research_interests": profile.research_interests,
                "orcid_id": profile.orcid_id,
                "verified": profile.verified,
                "available_for_meetings": profile.available_for_meetings
            })
    
    # If no collaborators found, return suggested ones
    if len(collaborators) == 0:
        suggested = db.query(User, ResearcherProfile).join(ResearcherProfile).filter(
            User.id != current_user.id,
            User.role == "researcher"
        ).distinct(User.id).limit(6).all()
        
        for user, profile in suggested:
            collaborators.append({
                "id": user.id,
                "name": user.full_name,
                "specialty": profile.specialty or "Research",
                "institution": profile.institution or "Not specified",
                "projects": 0,
                "status": "suggested",
                "research_interests": profile.research_interests,
                "orcid_id": profile.orcid_id,
                "verified": profile.verified,
                "available_for_meetings": profile.available_for_meetings
            })
    
    return {"collaborators": collaborators, "count": len(collaborators)}

@router.get("/suggested-collaborators")
async def get_suggested_collaborators(
    specialty: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get suggested collaborators based on researcher's specialty"""
    if current_user.role.value != "researcher":
        return {"collaborators": [], "count": 0}
    
    # Get current user's profile
    my_profile = db.query(ResearcherProfile).filter(
        ResearcherProfile.user_id == current_user.id
    ).first()
    
    search_specialty = specialty or (my_profile.specialty if my_profile else None)
    
    # Find other researchers with similar specialty
    query = db.query(User, ResearcherProfile).join(ResearcherProfile).filter(
        User.id != current_user.id,
        User.role == "researcher"
    )
    
    if search_specialty:
        query = query.filter(ResearcherProfile.specialty.contains(search_specialty))
    
    results = query.limit(20).all()
    
    # Exclude already connected researchers
    existing_follows = db.query(Follow.followed_id).filter(
        Follow.follower_id == current_user.id
    ).all()
    existing_ids = {f[0] for f in existing_follows}
    
    collaborators = []
    for user, profile in results:
        if user.id not in existing_ids:
            collaborators.append({
                "id": user.id,
                "name": user.full_name,
                "specialty": profile.specialty or "Research",
                "institution": profile.institution or "Not specified",
                "projects": 0,
                "status": "suggested",
                "research_interests": profile.research_interests,
                "orcid_id": profile.orcid_id,
                "verified": profile.verified,
                "available_for_meetings": profile.available_for_meetings
            })
    
    return {"collaborators": collaborators, "count": len(collaborators)}
