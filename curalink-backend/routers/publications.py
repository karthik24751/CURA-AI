from fastapi import APIRouter, Depends, Query
from typing import Optional

from auth_utils import get_current_user
from models import User
from services.api_integrations import PubMedService

router = APIRouter()

@router.get("/search")
async def search_publications(
    query: str = Query(..., min_length=1),
    max_results: int = Query(20, le=50),
    date_from: Optional[str] = Query(None)  # YYYY-MM-DD format
):
    """Search for medical publications with date filtering"""
    # Date filtering will be handled within PubMed query if provided
    search_term = query
    if date_from:
        search_term = f"{query} AND (\"{date_from}\"[Date - Publication] : \"3000\"[Date - Publication])"
    
    publications = await PubMedService.search_publications(search_term, max_results)
    
    # Add basic relevance scores without AI
    for pub in publications:
        # Use simple keyword matching for relevance score
        query_lower = query.lower()
        pub_text = f"{pub.get('title', '')} {pub.get('abstract', '')}".lower()
        
        # Simple keyword matching
        if query_lower in pub_text:
            pub['relevance_score'] = 90
        elif any(word in pub_text for word in query_lower.split()):
            pub['relevance_score'] = 75
        else:
            pub['relevance_score'] = 60
        
        # Calculate relevance reason based on query match
        title_lower = pub.get("title", "").lower()
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Simple relevance scoring
        score = 0
        for word in query_words:
            if word in title_lower:
                score += 20
        
        pub["match_score"] = min(95, 60 + score)  # Base 60, cap at 95
        pub["match_reason"] = f"Relevant to '{query}' - Published {pub.get('pub_date', 'Recently')}"
    
    return {"publications": publications, "count": len(publications)}

@router.get("/{pmid}")
async def get_publication_details(
    pmid: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific publication"""
    publications = await PubMedService.search_publications(pmid, max_results=1)
    
    if publications:
        pub = publications[0]
        if pub.get("abstract"):
            pub["ai_summary"] = await ai_service.summarize_publication(
                pub.get("title", ""),
                pub.get("abstract", "")
            )
        return pub
    
    return {"error": "Publication not found"}
