from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models import User, MeetingRequest
from schemas import MeetingRequestCreate, MeetingRequestResponse
from auth_utils import get_current_user
from routers.notifications import create_meeting_notification
from websocket_manager import manager
import json

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_meeting_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all meeting requests for the current user"""
    if current_user.role == "patient":
        # Get requests sent by patient
        requests = db.query(MeetingRequest, User).join(
            User, MeetingRequest.expert_id == User.id
        ).filter(MeetingRequest.requester_id == current_user.id).all()
        
        return [{
            "id": req.id,
            "expert": {
                "id": expert.id,
                "full_name": expert.full_name,
                "role": expert.role
            },
            "message": req.message,
            "status": req.status,
            "created_at": req.created_at,
            "type": "sent"
        } for req, expert in requests]
    else:
        # Get requests received by researcher
        requests = db.query(MeetingRequest, User).join(
            User, MeetingRequest.requester_id == User.id
        ).filter(MeetingRequest.expert_id == current_user.id).all()
        
        return [{
            "id": req.id,
            "requester": {
                "id": requester.id,
                "full_name": requester.full_name,
                "role": requester.role
            },
            "message": req.message,
            "status": req.status,
            "created_at": req.created_at,
            "type": "received"
        } for req, requester in requests]

@router.post("/", response_model=MeetingRequestResponse)
async def create_meeting_request(
    request_data: MeetingRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a meeting request"""
    # Check if target user exists
    target_user = db.query(User).filter(User.id == request_data.expert_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    # Prevent self-meetings
    if current_user.id == request_data.expert_id:
        raise HTTPException(status_code=400, detail="Cannot request meeting with yourself")
    
    # Check if request already exists
    existing = db.query(MeetingRequest).filter(
        MeetingRequest.requester_id == current_user.id,
        MeetingRequest.expert_id == request_data.expert_id,
        MeetingRequest.status == "pending"
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Meeting request already pending")
    
    meeting_request = MeetingRequest(
        requester_id=current_user.id,
        expert_id=request_data.expert_id,
        message=request_data.message
    )
    db.add(meeting_request)
    db.commit()
    db.refresh(meeting_request)
    
    # Create notification for the expert
    await create_meeting_notification(
        db=db,
        user_id=str(request_data.expert_id),
        notification_type="meeting_request",
        title="New Meeting Request",
        message=f"{current_user.full_name} has requested a meeting with you",
        from_user=current_user.full_name,
        meeting_id=meeting_request.id
    )
    
    # Send notification via WebSocket
    await manager.send_personal_message(
        str(request_data.expert_id),
        json.dumps({
            "type": "meeting_request",
            "request": {
                "id": meeting_request.id,
                "requester": {
                    "id": current_user.id,
                    "full_name": current_user.full_name,
                    "role": current_user.role
                },
                "message": meeting_request.message,
                "created_at": meeting_request.created_at.isoformat()
            }
        })
    )
    
    return meeting_request

@router.put("/{request_id}/status")
async def update_meeting_status(
    request_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update meeting request status (accept/reject)
    
    - Both expert and requester can update the status
    - Expert can accept/reject the meeting
    - Requester can cancel the meeting
    """
    meeting_request = db.query(MeetingRequest).filter(
        MeetingRequest.id == request_id
    ).first()
    
    if not meeting_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting request not found"
        )
    
    # Check if current user is either the expert or the requester
    if meeting_request.expert_id != current_user.id and meeting_request.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this meeting request"
        )
    
    new_status = status_data.get("status", "").lower()
    
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status field is required and must be 'accepted', 'rejected', or 'cancelled'"
        )
    
    # Normalize status values
    if new_status in ["declined", "reject"]:
        new_status = "rejected"
    elif new_status in ["cancel", "cancelled"]:
        new_status = "cancelled"
    
    # Validate status transition
    if meeting_request.status == "accepted" and new_status not in ["cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An accepted meeting can only be cancelled"
        )
    
    if new_status not in ["accepted", "rejected", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{new_status}'. Must be 'accepted', 'rejected', or 'cancelled'"
        )
    
    meeting_request.status = new_status
    db.commit()
    
    # Create notification for the requester
    notification_type = "meeting_accepted" if new_status == "accepted" else "meeting_declined"
    notification_title = f"Meeting Request {new_status.title()}"
    notification_message = f"{current_user.full_name} has {new_status} your meeting request"
    
    await create_meeting_notification(
        db=db,
        user_id=str(meeting_request.requester_id),
        notification_type=notification_type,
        title=notification_title,
        message=notification_message,
        from_user=current_user.full_name,
        meeting_id=meeting_request.id
    )
    
    # Notify requester via WebSocket
    await manager.send_personal_message(
        str(meeting_request.requester_id),
        json.dumps({
            "type": "meeting_status_update",
            "request": {
                "id": meeting_request.id,
                "status": new_status,
                "expert": {
                    "id": current_user.id,
                    "full_name": current_user.full_name
                }
            }
        })
    )
    
@router.post("/video-call")
async def initiate_video_call(
    call_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initiate a video call to another user"""
    target_user_id = call_data.get("target_user_id")
    room_name = call_data.get("room_name")

    if not target_user_id or not room_name:
        raise HTTPException(status_code=400, detail="target_user_id and room_name required")

    # Check if meeting exists and is accepted
    meeting = db.query(MeetingRequest).filter(
        ((MeetingRequest.requester_id == current_user.id) & (MeetingRequest.expert_id == target_user_id)) |
        ((MeetingRequest.requester_id == target_user_id) & (MeetingRequest.expert_id == current_user.id)),
        MeetingRequest.status == "accepted"
    ).first()

    if not meeting:
        raise HTTPException(status_code=403, detail="No accepted meeting found between users")

    # Send video call notification via WebSocket
    await manager.send_personal_message(
        str(target_user_id),
        json.dumps({
            "type": "video_call",
            "from": str(current_user.id),
            "caller_name": current_user.full_name,
            "room_name": room_name,
            "timestamp": datetime.utcnow().isoformat()
        })
    )

    return {"message": "Video call initiated", "room_name": room_name}

@router.delete("/{request_id}")
async def cancel_meeting_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a meeting request"""
    meeting_request = db.query(MeetingRequest).filter(
        MeetingRequest.id == request_id
    ).first()
    
    if not meeting_request:
        raise HTTPException(status_code=404, detail="Meeting request not found")
    
    # Allow both requester and expert to delete the meeting
    if meeting_request.requester_id != current_user.id and meeting_request.expert_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this meeting")
    
    db.delete(meeting_request)
    db.commit()
    
    return {"message": "Meeting request cancelled"}
