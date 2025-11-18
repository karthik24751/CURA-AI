from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from auth_utils import get_current_user
from models import User, Follow, Notification
from schemas import Follow as FollowSchema, FollowCreate
from websocket_manager import manager
import json

router = APIRouter()

@router.post("/", response_model=FollowSchema)
async def follow_user(
    follow_data: FollowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a follow request to another user"""
    if follow_data.followed_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if already following or request pending
    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followed_id == follow_data.followed_id
    ).first()
    
    if existing:
        # Use getattr to properly access the status attribute
        existing_status = getattr(existing, 'status', None)
        if existing_status == "accepted":
            raise HTTPException(status_code=400, detail="Already following this user")
        elif existing_status == "pending":
            raise HTTPException(status_code=400, detail="Follow request already pending")
    
    # Create follow request
    follow = Follow(
        follower_id=current_user.id,
        followed_id=follow_data.followed_id,
        status="pending" if current_user.role.value == "patient" else "accepted"  # Auto-accept if researcher following
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)
    
    # Create notification for the followed user
    followed_user = db.query(User).filter(User.id == follow_data.followed_id).first()
    if followed_user:
        notification = Notification(
            user_id=follow_data.followed_id,
            type="follow_request",
            title="New Follow Request",
            message=f"{current_user.full_name} wants to follow you",
            from_user=current_user.full_name
        )
        db.add(notification)
        db.commit()
        
        # Broadcast notification
        await manager.broadcast(json.dumps({
            "type": "notification",
            "user_id": follow_data.followed_id,
            "notification": {
                "id": notification.id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "from_user": notification.from_user
            }
        }))
    
    return follow

@router.put("/{follow_id}/respond")
async def respond_to_follow_request(
    follow_id: int,
    action: str,  # "accept" or "decline"
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accept or decline a follow request"""
    follow = db.query(Follow).filter(Follow.id == follow_id).first()
    if not follow:
        raise HTTPException(status_code=404, detail="Follow request not found")
    
    # Use proper comparison
    if getattr(follow, 'followed_id', None) != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to respond to this request")
    
    if action not in ["accept", "decline"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Use setattr to properly set the status attribute
    setattr(follow, 'status', "accepted" if action == "accept" else "declined")
    db.commit()
    
    # Create notification for the follower
    follower = db.query(User).filter(User.id == follow.follower_id).first()
    if follower:
        notification = Notification(
            user_id=follow.follower_id,
            type="follow_response",
            title=f"Follow Request {'Accepted' if action == 'accept' else 'Declined'}",
            message=f"{current_user.full_name} has {action}ed your follow request",
            from_user=current_user.full_name
        )
        db.add(notification)
        db.commit()
        
        # Broadcast notification
        await manager.broadcast(json.dumps({
            "type": "notification",
            "user_id": follow.follower_id,
            "notification": {
                "id": notification.id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "from_user": notification.from_user
            }
        }))
    
    return {"message": f"Follow request {action}ed"}

@router.delete("/{follow_id}")
async def unfollow_user(
    follow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unfollow a user"""
    follow = db.query(Follow).filter(Follow.id == follow_id).first()
    if not follow:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    
    # Use proper comparison
    if getattr(follow, 'follower_id', None) != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to unfollow")
    
    db.delete(follow)
    db.commit()
    
    return {"message": "Unfollowed successfully"}

@router.get("/following")
async def get_following(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get users that current user is following"""
    follows = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.status == "accepted"
    ).all()
    
    following = []
    for follow in follows:
        user = db.query(User).filter(User.id == follow.followed_id).first()
        if user:
            following.append({
                "id": user.id,
                "full_name": user.full_name,
                "role": user.role
            })
    
    return {"following": following}

@router.get("/followers")
async def get_followers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get users following current user"""
    follows = db.query(Follow).filter(
        Follow.followed_id == current_user.id,
        Follow.status == "accepted"
    ).all()
    
    followers = []
    for follow in follows:
        user = db.query(User).filter(User.id == follow.follower_id).first()
        if user:
            followers.append({
                "id": user.id,
                "full_name": user.full_name,
                "role": user.role
            })
    
    return {"followers": followers}

@router.get("/followers/{user_id}")
async def get_user_followers(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get users following a specific user"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get followers for this user
    follows = db.query(Follow).filter(
        Follow.followed_id == user_id,
        Follow.status == "accepted"
    ).all()
    
    followers = []
    for follow in follows:
        user = db.query(User).filter(User.id == follow.follower_id).first()
        if user:
            followers.append({
                "id": user.id,
                "full_name": user.full_name,
                "role": user.role
            })
    
    return {"followers": followers}

@router.get("/requests")
async def get_follow_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pending follow requests for current user"""
    requests = db.query(Follow, User).join(User, Follow.follower_id == User.id).filter(
        Follow.followed_id == current_user.id,
        Follow.status == "pending"
    ).all()
    
    result = []
    for follow, follower in requests:
        result.append({
            "id": follow.id,
            "follower": {
                "id": follower.id,
                "full_name": follower.full_name,
                "role": follower.role
            },
            "created_at": follow.created_at
        })
    
    return {"requests": result}
