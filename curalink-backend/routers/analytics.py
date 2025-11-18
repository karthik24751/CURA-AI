from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
import json

from database import get_db
from auth_utils import get_current_user
from models import User, UserActivity, DiseaseCategory, Rating, ResearcherProfile, Favorite
from services.ai_service import ai_service

router = APIRouter()

# Disease Prediction and Suggestions
@router.get("/diseases/suggest")
async def suggest_diseases(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Smart disease prediction with auto-suggestions"""
    query_lower = query.lower()
    
    # Common diseases database with related conditions
    disease_database = {
        "parkinson": {
            "name": "Parkinson's Disease",
            "related": ["Multiple System Atrophy", "Lewy Body Dementia", "Progressive Supranuclear Palsy", "Essential Tremor"],
            "keywords": ["tremor", "rigidity", "bradykinesia", "deep brain stimulation"]
        },
        "alzheimer": {
            "name": "Alzheimer's Disease",
            "related": ["Vascular Dementia", "Frontotemporal Dementia", "Mild Cognitive Impairment"],
            "keywords": ["memory loss", "dementia", "cognitive decline", "amyloid"]
        },
        "cancer": {
            "name": "Cancer",
            "related": ["Breast Cancer", "Lung Cancer", "Prostate Cancer", "Colorectal Cancer", "Melanoma"],
            "keywords": ["tumor", "oncology", "chemotherapy", "radiation", "immunotherapy"]
        },
        "diabetes": {
            "name": "Diabetes",
            "related": ["Type 1 Diabetes", "Type 2 Diabetes", "Gestational Diabetes", "Prediabetes"],
            "keywords": ["insulin", "glucose", "blood sugar", "hyperglycemia"]
        },
        "adhd": {
            "name": "ADHD",
            "related": ["ADD", "Executive Function Disorder", "Learning Disabilities"],
            "keywords": ["attention", "hyperactivity", "focus", "concentration"]
        },
        "depression": {
            "name": "Depression",
            "related": ["Major Depressive Disorder", "Bipolar Disorder", "Seasonal Affective Disorder"],
            "keywords": ["mood", "mental health", "antidepressant", "therapy"]
        },
        "heart": {
            "name": "Heart Disease",
            "related": ["Coronary Artery Disease", "Heart Failure", "Arrhythmia", "Hypertension"],
            "keywords": ["cardiac", "cardiovascular", "blood pressure", "cholesterol"]
        },
        "stroke": {
            "name": "Stroke",
            "related": ["Ischemic Stroke", "Hemorrhagic Stroke", "TIA", "Cerebrovascular Disease"],
            "keywords": ["cerebral", "brain attack", "thrombosis", "embolism"]
        },
        "multiple sclerosis": {
            "name": "Multiple Sclerosis",
            "related": ["Relapsing-Remitting MS", "Primary Progressive MS", "Neuromyelitis Optica"],
            "keywords": ["demyelination", "autoimmune", "neurological", "myelin"]
        },
        "asthma": {
            "name": "Asthma",
            "related": ["COPD", "Chronic Bronchitis", "Allergic Rhinitis"],
            "keywords": ["respiratory", "breathing", "wheezing", "bronchial"]
        }
    }
    
    suggestions = []
    
    # Find matching diseases
    for key, data in disease_database.items():
        if query_lower in key or query_lower in data["name"].lower():
            suggestions.append({
                "name": data["name"],
                "match_type": "primary",
                "related_conditions": data["related"],
                "keywords": data["keywords"]
            })
        elif any(query_lower in keyword for keyword in data["keywords"]):
            suggestions.append({
                "name": data["name"],
                "match_type": "keyword",
                "related_conditions": data["related"],
                "keywords": data["keywords"]
            })
    
    # Also check database for stored disease categories
    db_categories = db.query(DiseaseCategory).filter(
        DiseaseCategory.name.ilike(f"%{query}%")
    ).limit(5).all()
    
    for category in db_categories:
        related = json.loads(category.related_diseases) if category.related_diseases else []
        suggestions.append({
            "name": category.name,
            "match_type": "database",
            "related_conditions": related,
            "keywords": category.keywords.split(",") if category.keywords else []
        })
    
    # Update disease popularity
    if suggestions:
        existing = db.query(DiseaseCategory).filter(DiseaseCategory.name == suggestions[0]["name"]).first()
        if existing:
            existing.popularity_score = (existing.popularity_score or 0) + 1
        else:
            new_category = DiseaseCategory(
                name=suggestions[0]["name"],
                keywords=",".join(suggestions[0]["keywords"]),
                related_diseases=json.dumps(suggestions[0]["related_conditions"]),
                popularity_score=1
            )
            db.add(new_category)
        db.commit()
    
    return {
        "query": query,
        "suggestions": suggestions[:10],
        "count": len(suggestions)
    }

# Weekly Insights Dashboard
@router.get("/insights/weekly")
async def get_weekly_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get weekly insights for user activity"""
    week_ago = datetime.now() - timedelta(days=7)
    
    # Top viewed publications
    pub_views = db.query(UserActivity).filter(
        UserActivity.user_id == current_user.id,
        UserActivity.activity_type == 'view_publication',
        UserActivity.created_at >= week_ago
    ).all()
    
    # Top viewed trials
    trial_views = db.query(UserActivity).filter(
        UserActivity.user_id == current_user.id,
        UserActivity.activity_type == 'view_trial',
        UserActivity.created_at >= week_ago
    ).all()
    
    # New matches (favorites added this week)
    new_favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.created_at >= week_ago
    ).count()
    
    # Get top viewed items
    top_publications = []
    pub_counts = {}
    for view in pub_views:
        item_id = view.item_id
        pub_counts[item_id] = pub_counts.get(item_id, 0) + 1
    
    sorted_pubs = sorted(pub_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for pmid, count in sorted_pubs:
        matching_view = next((v for v in pub_views if v.item_id == pmid), None)
        if matching_view and matching_view.item_data:
            data = json.loads(matching_view.item_data)
            top_publications.append({
                "pmid": pmid,
                "title": data.get("title", "Unknown"),
                "views": count
            })
    
    # Top viewed trials
    top_trials = []
    trial_counts = {}
    for view in trial_views:
        item_id = view.item_id
        trial_counts[item_id] = trial_counts.get(item_id, 0) + 1
    
    sorted_trials = sorted(trial_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for nct_id, count in sorted_trials:
        matching_view = next((v for v in trial_views if v.item_id == nct_id), None)
        if matching_view and matching_view.item_data:
            data = json.loads(matching_view.item_data)
            top_trials.append({
                "nct_id": nct_id,
                "title": data.get("title", "Unknown"),
                "views": count
            })
    
    return {
        "period": "last_7_days",
        "summary": {
            "publications_viewed": len(pub_views),
            "trials_viewed": len(trial_views),
            "new_favorites": new_favorites,
            "total_activity": len(pub_views) + len(trial_views)
        },
        "top_publications": top_publications,
        "top_trials": top_trials,
        "new_matches": new_favorites
    }

# Publication Analytics Dashboard
@router.get("/analytics/publications")
async def get_publication_analytics(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get publication analytics and trends"""
    start_date = datetime.now() - timedelta(days=days)
    
    # Most active researchers (based on user views)
    researcher_views = db.query(
        UserActivity.item_id,
        func.count(UserActivity.id).label('view_count')
    ).filter(
        UserActivity.activity_type == 'view_expert',
        UserActivity.created_at >= start_date
    ).group_by(UserActivity.item_id).order_by(desc('view_count')).limit(10).all()
    
    active_researchers = []
    for item_id, count in researcher_views:
        try:
            researcher_id = int(item_id)
            user = db.query(User).filter(User.id == researcher_id).first()
            if user:
                profile = db.query(ResearcherProfile).filter(ResearcherProfile.user_id == researcher_id).first()
                active_researchers.append({
                    "id": researcher_id,
                    "name": user.full_name,
                    "specialty": profile.specialty if profile else "Unknown",
                    "views": count
                })
        except:
            continue
    
    # Trending diseases (most searched/viewed)
    trending_diseases = db.query(
        DiseaseCategory.name,
        DiseaseCategory.popularity_score
    ).filter(
        DiseaseCategory.created_at >= start_date
    ).order_by(desc(DiseaseCategory.popularity_score)).limit(10).all()
    
    # Publication growth (activity over time)
    daily_views = db.query(
        func.date(UserActivity.created_at).label('date'),
        func.count(UserActivity.id).label('count')
    ).filter(
        UserActivity.activity_type == 'view_publication',
        UserActivity.created_at >= start_date
    ).group_by(func.date(UserActivity.created_at)).all()
    
    publication_growth = [
        {"date": str(date), "count": count}
        for date, count in daily_views
    ]
    
    return {
        "period_days": days,
        "most_active_researchers": active_researchers,
        "trending_diseases": [
            {"name": name, "popularity": score}
            for name, score in trending_diseases
        ],
        "publication_growth": publication_growth,
        "total_views": sum(count for _, count in daily_views)
    }

# Disease Popularity Heatmap Data
@router.get("/analytics/disease-heatmap")
async def get_disease_heatmap(
    disease: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get disease popularity data for geographic heatmap"""
    
    # Regional activity data (simulated based on user locations and searches)
    regions = [
        {"region": "North America", "lat": 40.7128, "lng": -74.0060, "activity": 0},
        {"region": "Europe", "lat": 51.5074, "lng": -0.1278, "activity": 0},
        {"region": "Asia", "lat": 35.6762, "lng": 139.6503, "activity": 0},
        {"region": "South America", "lat": -23.5505, "lng": -46.6333, "activity": 0},
        {"region": "Africa", "lat": -1.2921, "lng": 36.8219, "activity": 0},
        {"region": "Oceania", "lat": -33.8688, "lng": 151.2093, "activity": 0}
    ]
    
    # Get activity counts based on disease searches
    if disease:
        category = db.query(DiseaseCategory).filter(DiseaseCategory.name.ilike(f"%{disease}%")).first()
        if category:
            # Distribute popularity across regions (weighted by general research activity)
            base_activity = category.popularity_score or 10
            regions[0]["activity"] = int(base_activity * 0.35)  # North America
            regions[1]["activity"] = int(base_activity * 0.30)  # Europe
            regions[2]["activity"] = int(base_activity * 0.20)  # Asia
            regions[3]["activity"] = int(base_activity * 0.08)  # South America
            regions[4]["activity"] = int(base_activity * 0.04)  # Africa
            regions[5]["activity"] = int(base_activity * 0.03)  # Oceania
    else:
        # Global overview
        total_diseases = db.query(func.sum(DiseaseCategory.popularity_score)).scalar() or 100
        regions[0]["activity"] = int(total_diseases * 0.35)
        regions[1]["activity"] = int(total_diseases * 0.30)
        regions[2]["activity"] = int(total_diseases * 0.20)
        regions[3]["activity"] = int(total_diseases * 0.08)
        regions[4]["activity"] = int(total_diseases * 0.04)
        regions[5]["activity"] = int(total_diseases * 0.03)
    
    return {
        "disease": disease or "All Diseases",
        "regions": regions,
        "total_activity": sum(r["activity"] for r in regions),
        "last_updated": datetime.now().isoformat()
    }

# Track user activity
@router.post("/activity/track")
async def track_activity(
    activity_type: str,
    item_type: str,
    item_id: str,
    item_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track user activity for analytics"""
    activity = UserActivity(
        user_id=current_user.id,
        activity_type=activity_type,
        item_type=item_type,
        item_id=item_id,
        item_data=json.dumps(item_data)
    )
    db.add(activity)
    db.commit()
    
    return {"status": "tracked", "activity_id": activity.id}

# Rating system
@router.post("/ratings/")
async def create_rating(
    item_type: str,
    item_id: str,
    rating: int = Query(..., ge=1, le=5),
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update a rating"""
    # Check if rating already exists
    existing = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.item_type == item_type,
        Rating.item_id == item_id
    ).first()
    
    if existing:
        existing.rating = rating
        existing.comment = comment
    else:
        new_rating = Rating(
            user_id=current_user.id,
            item_type=item_type,
            item_id=item_id,
            rating=rating,
            comment=comment
        )
        db.add(new_rating)
    
    db.commit()
    
    return {"status": "success", "rating": rating}

@router.get("/ratings/{item_type}/{item_id}")
async def get_ratings(
    item_type: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ratings for an item"""
    ratings = db.query(Rating).filter(
        Rating.item_type == item_type,
        Rating.item_id == item_id
    ).all()
    
    if not ratings:
        return {"average": 0, "count": 0, "ratings": []}
    
    avg_rating = sum(r.rating for r in ratings) / len(ratings)
    
    return {
        "average": round(avg_rating, 1),
        "count": len(ratings),
        "ratings": [
            {
                "id": r.id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat()
            }
            for r in ratings
        ]
    }
