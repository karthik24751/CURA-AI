from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from typing import List
import json

from database import engine, Base
from routers import auth, users, trials, publications, experts, forums, favorites, chat, meetings, notifications
try:
    from websocket_manager import manager
except ImportError:
    # Create a mock manager for serverless
    class MockManager:
        async def connect(self, user_id, websocket): pass
        async def disconnect(self, user_id): pass
        async def send_personal_message(self, user_id, message): pass
    manager = MockManager()

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️ Database creation warning: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 CuraLink Backend Starting...")
    yield
    # Shutdown
    print("👋 CuraLink Backend Shutting Down...")

app = FastAPI(
    title="CuraLink API",
    description="AI-Powered Healthcare Discovery Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(trials.router, prefix="/api/trials", tags=["Clinical Trials"])
app.include_router(publications.router, prefix="/api/publications", tags=["Publications"])
app.include_router(experts.router, prefix="/api/experts", tags=["Experts"])
app.include_router(forums.router, prefix="/api/forums", tags=["Forums"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["Meetings"])
app.include_router(notifications.router, tags=["Notifications"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to CuraLink API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "chat":
                await manager.send_personal_message(
                    message_data.get("to_user_id"),
                    json.dumps({
                        "type": "chat",
                        "from": user_id,
                        "message": message_data.get("message"),
                        "timestamp": message_data.get("timestamp")
                    })
                )
            elif message_data.get("type") == "notification":
                await manager.send_personal_message(
                    message_data.get("to_user_id"),
                    json.dumps({
                        "type": "notification",
                        "message": message_data.get("message"),
                        "timestamp": message_data.get("timestamp")
                    })
                )
    except WebSocketDisconnect:
        manager.disconnect(user_id)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    reload = os.environ.get("RELOAD", "false").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=reload)
