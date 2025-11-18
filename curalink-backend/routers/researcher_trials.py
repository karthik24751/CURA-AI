from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from auth_utils import get_current_user
from models import User, ClinicalTrial
from services.api_integrations import ClinicalTrialsService

router = APIRouter()

@router.get("/my-trials")
async def get_my_trials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get clinical trials managed by the current researcher"""
    if current_user.role.value != "researcher":
        raise HTTPException(status_code=403, detail="Only researchers can access this endpoint")
    
    # Get trials from database where researcher is the PI
    db_trials = db.query(ClinicalTrial).filter(
        ClinicalTrial.principal_investigator == current_user.full_name
    ).all()
    
    trials = []
    for trial in db_trials:
        trials.append({
            "id": trial.id,
            "nct_id": trial.nct_id,
            "title": trial.title,
            "phase": trial.phase,
            "status": trial.status,
            "condition": trial.condition,
            "participants": trial.current_enrollment or 0,
            "target": trial.target_enrollment or 0,
            "startDate": str(trial.start_date) if trial.start_date else None,
            "location": trial.location,
            "sponsor": trial.sponsor,
            "description": trial.description
        })
    
    return {"trials": trials, "count": len(trials)}

@router.get("/nearby-trials")
async def get_nearby_trials(
    location: Optional[str] = Query(None),
    specialty: Optional[str] = Query(None),
    max_results: int = Query(10, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get clinical trials near researcher's location or in their specialty"""
    if current_user.role.value != "researcher":
        raise HTTPException(status_code=403, detail="Only researchers can access this endpoint")
    
    # Get researcher's profile for location and specialty
    from models import ResearcherProfile
    profile = db.query(ResearcherProfile).filter(
        ResearcherProfile.user_id == current_user.id
    ).first()
    
    search_location = location or (profile.institution if profile else None)
    search_condition = specialty or (profile.specialty if profile else None)
    
    # Fetch trials from ClinicalTrials.gov
    trials = await ClinicalTrialsService.search_trials(
        condition=search_condition,
        location=search_location,
        max_results=max_results
    )
    
    return {"trials": trials, "count": len(trials)}

@router.post("/track-trial")
async def track_trial(
    trial_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a trial to researcher's tracked trials"""
    if current_user.role.value != "researcher":
        raise HTTPException(status_code=403, detail="Only researchers can track trials")
    
    # Check if trial already exists
    existing = db.query(ClinicalTrial).filter(
        ClinicalTrial.nct_id == trial_data.get("nct_id")
    ).first()
    
    if existing:
        return {"message": "Trial already tracked", "trial": existing}
    
    # Create new trial record
    trial = ClinicalTrial(
        nct_id=trial_data.get("nct_id"),
        title=trial_data.get("title"),
        phase=trial_data.get("phase"),
        status=trial_data.get("status"),
        condition=trial_data.get("condition"),
        principal_investigator=current_user.full_name,
        current_enrollment=trial_data.get("participants", 0),
        target_enrollment=trial_data.get("target", 0),
        location=trial_data.get("location"),
        sponsor=trial_data.get("sponsor"),
        description=trial_data.get("description"),
        start_date=datetime.fromisoformat(trial_data["startDate"]) if trial_data.get("startDate") else None
    )
    
    db.add(trial)
    db.commit()
    db.refresh(trial)
    
    return {"message": "Trial tracked successfully", "trial": trial}
