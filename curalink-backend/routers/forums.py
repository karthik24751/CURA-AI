from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from auth_utils import get_current_user
from models import User, Forum, ForumPost
from schemas import (
    Forum as ForumSchema,
    ForumCreate,
    ForumPost as ForumPostSchema,
    ForumPostCreate,
    ForumPostUpdate
)
from websocket_manager import manager
import json

router = APIRouter()

# Disease categories for forums
DISEASE_CATEGORIES = [
    "ADHD Discussions",
    "Alzheimer's & Dementia",
    "Breast Cancer Updates",
    "Cancer Research",
    "Cardiovascular Health",
    "Diabetes Management",
    "Mental Health",
    "Neurology",
    "Parkinson's Disease",
    "Rare Diseases",
    "General Health",
    "Clinical Trials",
    "Research Methods"
]

@router.get("/categories")
async def get_categories(current_user: User = Depends(get_current_user)):
    """Get all available disease categories for forums"""
    return {"categories": DISEASE_CATEGORIES}

@router.get("/", response_model=List[ForumSchema])
async def get_forums(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all forums, optionally filtered by category"""
    query = db.query(Forum)
    
    if category:
        query = query.filter(Forum.category == category)
    
    forums = query.order_by(Forum.created_at.desc()).all()
    
    # Add post_count and member_count to each forum
    for forum in forums:
        forum.post_count = db.query(ForumPost).filter(ForumPost.forum_id == forum.id).count()
        forum.member_count = 50  # Placeholder value, would need to implement actual member tracking
    
    return forums

@router.post("/", response_model=ForumSchema)
async def create_forum(
    forum_data: ForumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new forum (researchers only)"""
    if current_user.role.value != "researcher":
        raise HTTPException(status_code=403, detail="Only researchers can create forums")
    
    # Set the created_by field to the current user's ID
    forum = Forum(**forum_data.dict(), created_by=current_user.id)
    db.add(forum)
    db.commit()
    db.refresh(forum)
    
    # Broadcast new forum to all connected users
    await manager.broadcast(json.dumps({
        "type": "new_forum",
        "forum": {
            "id": forum.id,
            "title": forum.title,
            "description": forum.description,
            "category": forum.category
        }
    }))
    
    return forum

@router.get("/{forum_id}/posts")
async def get_forum_posts(
    forum_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all posts in a forum"""
    posts = db.query(ForumPost, User).join(User).filter(
        ForumPost.forum_id == forum_id,
        ForumPost.parent_id == None  # Only top-level posts
    ).all()
    
    result = []
    for post, author in posts:
        # Get replies
        replies = db.query(ForumPost, User).join(User).filter(
            ForumPost.parent_id == post.id
        ).all()
        
        result.append({
            "id": post.id,
            "content": post.content,
            "created_at": post.created_at,
            "author": {
                "id": author.id,
                "full_name": author.full_name,
                "role": author.role
            },
            "replies": [{
                "id": reply.id,
                "content": reply.content,
                "created_at": reply.created_at,
                "author": {
                    "id": reply_author.id,
                    "full_name": reply_author.full_name,
                    "role": reply_author.role
                }
            } for reply, reply_author in replies]
        })
    
    return result

@router.post("/{forum_id}/posts", response_model=ForumPostSchema)
async def create_post(
    forum_id: int,
    post_data: ForumPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new post in a forum"""
    # Patients can create posts, researchers can create posts and replies
    if post_data.parent_id and current_user.role.value == "patient":
        raise HTTPException(status_code=403, detail="Only researchers can reply to posts")
    
    post = ForumPost(
        forum_id=forum_id,
        author_id=current_user.id,
        content=post_data.content,
        parent_id=post_data.parent_id
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # Broadcast new post to all connected users
    await manager.broadcast(json.dumps({
        "type": "new_post",
        "forum_id": forum_id,
        "post": {
            "id": post.id,
            "content": post.content,
            "author": {
                "id": current_user.id,
                "full_name": current_user.full_name,
                "role": current_user.role
            },
            "parent_id": post.parent_id
        }
    }))
    
    return post

@router.put("/{forum_id}/posts/{post_id}")
async def update_post(
    forum_id: int,
    post_id: int,
    post_data: ForumPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a post (only author can edit)"""
    # Query for the post and check ownership in one query
    post = db.query(ForumPost).filter(
        ForumPost.id == post_id,
        ForumPost.forum_id == forum_id,
        ForumPost.author_id == current_user.id  # Check ownership in the query
    ).first()
    
    if not post:
        # We don't know if the post doesn't exist or if the user doesn't own it
        # Let's check if the post exists at all
        post_exists = db.query(ForumPost).filter(
            ForumPost.id == post_id,
            ForumPost.forum_id == forum_id
        ).first()
        
        if not post_exists:
            raise HTTPException(status_code=404, detail="Post not found")
        else:
            raise HTTPException(status_code=403, detail="You can only edit your own posts")
    
    # Update the content using setattr to avoid direct assignment issues
    setattr(post, 'content', post_data.content)
    db.commit()
    db.refresh(post)
    
    # Broadcast post update
    await manager.broadcast(json.dumps({
        "type": "post_updated",
        "forum_id": forum_id,
        "post": {
            "id": post.id,
            "content": post.content,
            "updated_at": str(post.updated_at)
        }
    }))
    
    return post

@router.delete("/{forum_id}/posts/{post_id}")
async def delete_post(
    forum_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a post (only author can delete)"""
    # Query for the post and check ownership in one query
    post = db.query(ForumPost).filter(
        ForumPost.id == post_id,
        ForumPost.forum_id == forum_id,
        ForumPost.author_id == current_user.id  # Check ownership in the query
    ).first()
    
    if not post:
        # We don't know if the post doesn't exist or if the user doesn't own it
        # Let's check if the post exists at all
        post_exists = db.query(ForumPost).filter(
            ForumPost.id == post_id,
            ForumPost.forum_id == forum_id
        ).first()
        
        if not post_exists:
            raise HTTPException(status_code=404, detail="Post not found")
        else:
            raise HTTPException(status_code=403, detail="You can only delete your own posts")
    
    db.delete(post)
    db.commit()
    
    # Broadcast post deletion
    await manager.broadcast(json.dumps({
        "type": "post_deleted",
        "forum_id": forum_id,
        "post_id": post_id
    }))
    
    return {"message": "Post deleted successfully"}
