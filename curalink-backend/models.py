from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(str, enum.Enum):
    PATIENT = "patient"
    RESEARCHER = "researcher"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
    researcher_profile = relationship("ResearcherProfile", back_populates="user", uselist=False)
    favorites = relationship("Favorite", back_populates="user")
    forum_posts = relationship("ForumPost", back_populates="author")
    sent_messages = relationship("ChatMessage", foreign_keys="ChatMessage.sender_id", back_populates="sender")
    received_messages = relationship("ChatMessage", foreign_keys="ChatMessage.receiver_id", back_populates="receiver")
    meeting_requests_sent = relationship("MeetingRequest", foreign_keys="MeetingRequest.requester_id", back_populates="requester")
    meeting_requests_received = relationship("MeetingRequest", foreign_keys="MeetingRequest.expert_id", back_populates="expert")
    notifications = relationship("Notification", back_populates="user")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")
    followers = relationship("Follow", foreign_keys="Follow.followed_id", back_populates="followed")

class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    medical_condition = Column(String(500))
    location = Column(String(255))
    age = Column(Integer)
    additional_info = Column(Text)
    
    user = relationship("User", back_populates="patient_profile")

class ResearcherProfile(Base):
    __tablename__ = "researcher_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    specialty = Column(String(255))
    research_interests = Column(Text)
    institution = Column(String(255))
    orcid_id = Column(String(100))
    publications_summary = Column(Text)
    available_for_meetings = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="researcher_profile")

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_type = Column(String(50))  # 'trial', 'publication', 'expert'
    item_id = Column(String(255))
    item_data = Column(Text)  # JSON string of the saved item
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="favorites")

class Follow(Base):
    __tablename__ = "follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # User who is following
    followed_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # User being followed
    status = Column(String(20), default="pending")  # 'pending', 'accepted', 'declined'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")

class Forum(Base):
    __tablename__ = "forums"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    created_by = Column(Integer, ForeignKey("users.id"))  # Add this field
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    posts = relationship("ForumPost", back_populates="forum")
    creator = relationship("User")  # Add this relationship

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")

class ForumPost(Base):
    __tablename__ = "forum_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    forum_id = Column(Integer, ForeignKey("forums.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=True)  # For replies
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    forum = relationship("Forum", back_populates="posts")
    author = relationship("User", back_populates="forum_posts")
    replies = relationship("ForumPost", remote_side=[id])

class MeetingRequest(Base):
    __tablename__ = "meeting_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"))
    expert_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    status = Column(String(50), default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    requester = relationship("User", foreign_keys=[requester_id], back_populates="meeting_requests_sent")
    expert = relationship("User", foreign_keys=[expert_id], back_populates="meeting_requests_received")

class ClinicalTrial(Base):
    __tablename__ = "clinical_trials"
    
    id = Column(Integer, primary_key=True, index=True)
    nct_id = Column(String(50), unique=True, index=True)
    title = Column(String(500))
    summary = Column(Text)
    ai_summary = Column(Text)
    description = Column(Text)
    condition = Column(String(255))
    location = Column(String(255))
    phase = Column(String(50))
    status = Column(String(100))
    sponsor = Column(String(255))
    principal_investigator = Column(String(255))
    current_enrollment = Column(Integer, default=0)
    target_enrollment = Column(Integer, default=0)
    start_date = Column(DateTime(timezone=True))
    data = Column(Text)  # Full JSON data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String(50))  # 'meeting_request', 'meeting_accepted', 'meeting_declined', 'general'
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    from_user = Column(String(255))  # Name of the user who triggered the notification
    meeting_id = Column(Integer, nullable=True)  # Reference to meeting request if applicable
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="notifications")

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_type = Column(String(50), nullable=False)  # 'publication', 'expert_response', 'trial'
    item_id = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="ratings")

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # 'view_publication', 'view_trial', 'view_expert'
    item_type = Column(String(50), nullable=False)
    item_id = Column(String(255), nullable=False)
    item_data = Column(Text)  # JSON data about the item
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="activities")

class DiseaseCategory(Base):
    __tablename__ = "disease_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    keywords = Column(Text)  # Comma-separated keywords
    related_diseases = Column(Text)  # JSON array of related disease names
    popularity_score = Column(Integer, default=0)  # Track how often searched
    created_at = Column(DateTime(timezone=True), server_default=func.now())
