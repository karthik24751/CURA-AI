from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from auth_utils import get_current_user
from models import User
from services.api_integrations import ClinicalTrialsService

router = APIRouter()

@router.get("/search")
async def search_trials(
    condition: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    phase: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    max_results: int = Query(20, le=50)
):
    """Search for clinical trials"""
    try:
        trials = await ClinicalTrialsService.search_trials(
            condition=condition,
            location=location,
            phase=phase,
            status=status,
            max_results=max_results
        )
    except Exception as e:
        print(f"ClinicalTrials API failed: {e}")
        # Return empty list when API fails - no mock data
        trials = []

    # Add basic match score without AI
    for trial in trials:
        # Use simple keyword matching for match score
        if condition:
            condition_lower = condition.lower()
            trial_text = f"{trial.get('title', '')} {trial.get('summary', '')} {trial.get('condition', '')}".lower()

            # Simple keyword matching
            if condition_lower in trial_text:
                trial['match_score'] = 90
            elif any(word in trial_text for word in condition_lower.split()):
                trial['match_score'] = 75
            else:
                trial['match_score'] = 60
        else:
            trial['match_score'] = 75  # Default score based on condition and location

        # Calculate match score based on condition and location
        score = 70  # Base score

        if condition:
            trial_condition = trial.get("condition", "").lower()
            if condition.lower() in trial_condition:
                score += 20

        if location:
            trial_locations = trial.get("locations", [])
            if any(location.lower() in loc.lower() for loc in trial_locations):
                score += 10

        trial["match_score"] = min(score, 95)

        # Generate match reason
        reasons = []
        if trial.get("phase"):
            reasons.append(f"Phase {trial['phase']}")
        if trial.get("status"):
            reasons.append(trial["status"])
        if trial.get("locations"):
            reasons.append(f"Available in {len(trial['locations'])} locations")

        trial["match_reason"] = " - ".join(reasons) if reasons else "Clinical trial match"

        # Add enrollment progress if available
        if trial.get("enrollment"):
            trial["enrollment_progress"] = {
                "current": trial["enrollment"],
                "target": trial["enrollment"],  # In real implementation, get target from trial data
                "percentage": 0  # Real data would calculate this based on current vs target enrollment
            }

    return trials

@router.get("/{nct_id}")
async def get_trial_details(
    nct_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific trial"""
    trials = await ClinicalTrialsService.search_trials(max_results=1)
    
    # In a real implementation, you'd fetch by NCT ID
    # For now, return first result as example
    if trials:
        trial = trials[0]
        trial["ai_summary"] = await ai_service.summarize_clinical_trial(
            trial.get("title", ""),
            trial.get("summary", ""),
            trial.get("detailed_description", "")
        )
        return trial
    
    return {"error": "Trial not found"}
