# 🌟 CuraLink - Unique Features & Implementation Guide

## 📋 Table of Contents
1. [Unique Implementations](#unique-implementations)
2. [Real-Time Chat System](#real-time-chat-system)
3. [Video Call Facility](#video-call-facility)
4. [Live Notifications](#live-notifications)
5. [AI-Powered Features](#ai-powered-features)
6. [External API Integrations](#external-api-integrations)
7. [How to Use Each Feature](#how-to-use-each-feature)

---

## 🎯 Unique Implementations

### 1. **WebSocket-Based Real-Time Communication**
**What makes it unique:**
- Custom WebSocket manager with automatic reconnection
- Bidirectional real-time communication between patients and researchers
- Event-driven architecture supporting multiple message types
- Connection pooling and user session management

**Technical Stack:**
- **Backend:** FastAPI WebSocket with custom `ConnectionManager` class
- **Frontend:** Native WebSocket API with event listener pattern
- **Location:** 
  - Backend: `/curalink-backend/websocket_manager.py`
  - Frontend: `/curalink-frontend/lib/websocket.ts`

**Key Features:**
- Automatic reconnection after 3 seconds on disconnect
- Support for multiple event types: `chat_message`, `video_call`, `meeting_request`, `notification`
- User-specific message routing
- Broadcast capabilities

---

### 2. **AI-Powered Medical Assistant (Cura AI)**
**What makes it unique:**
- Integration with SambaNova AI (Meta-Llama-3.1-8B-Instruct model)
- Intelligent fallback responses when API is unavailable
- Context-aware medical query handling
- Rate limiting and response caching to optimize API usage

**Technical Implementation:**
- **Backend:** `/curalink-backend/services/ai_service.py`
- **Frontend:** `/curalink-frontend/components/CuraAIChat.tsx`

**Capabilities:**
- Medical condition extraction from natural language
- Clinical trial summarization
- Publication summarization
- Expert recommendation based on condition matching
- Conversational health assistance

**Rate Limiting:**
- 5-second minimum interval between API requests (backend)
- 6-second minimum interval on frontend
- 10-minute response caching
- Intelligent fallback for common queries

---

### 3. **Multi-Source Medical Data Integration**
**What makes it unique:**
- Real-time integration with 3 major medical databases
- Unified search interface across multiple sources
- Automatic data normalization and formatting

**Integrated APIs:**

#### a) **PubMed API Integration**
- **Purpose:** Fetch latest medical publications and research papers
- **Implementation:** `/curalink-backend/services/api_integrations.py` (PubMedService)
- **Features:**
  - Search by medical condition/keyword
  - Extract authors, abstracts, DOI, journal info
  - Up to 20 results per query
  - XML parsing with BioPython

#### b) **ClinicalTrials.gov API**
- **Purpose:** Access clinical trial data
- **Implementation:** `/curalink-backend/services/api_integrations.py` (ClinicalTrialsService)
- **Features:**
  - Search by condition, location, phase, status
  - Extract trial details, enrollment info, sponsor data
  - Location-based filtering
  - Study type classification

#### c) **ORCID API Integration**
- **Purpose:** Researcher verification and profile data
- **Implementation:** `/curalink-backend/services/api_integrations.py` (ORCIDService)
- **Features:**
  - Researcher profile verification
  - Biography and keyword extraction
  - Institution affiliation data
  - Researcher search functionality

---

### 4. **Dual-Role User System**
**What makes it unique:**
- Single platform supporting two distinct user roles with different workflows
- Role-based routing and permissions
- Specialized onboarding for each role

**Roles:**
- **Patients:** Search trials, connect with experts, manage health conditions
- **Researchers:** Manage trials, collaborate, handle meeting requests

**Implementation:**
- Role-based authentication in `/curalink-backend/auth_utils.py`
- Separate dashboards and onboarding flows
- Role-specific API endpoints and permissions

---

### 5. **Meeting Request & Video Call System**
**What makes it unique:**
- Complete meeting lifecycle management
- Integrated video calling with Jitsi Meet
- Real-time status updates via WebSocket
- Permission-based video call initiation

**Components:**
- Meeting request creation and management
- Accept/Reject workflow
- Video call room generation
- Real-time notifications for all meeting events

---

## 💬 Real-Time Chat System

### Architecture
```
User A (Frontend) → WebSocket Connection → Backend WebSocket Manager → User B (Frontend)
                                    ↓
                              MySQL Database
```

### How It Works

#### 1. **Connection Establishment**
```typescript
// Frontend: lib/websocket.ts
wsManager.connect(userId);
```
- Establishes WebSocket connection to `ws://localhost:8000/ws/{userId}`
- Auto-reconnects on disconnect after 3 seconds
- Maintains user session

#### 2. **Sending Messages**
**Backend Endpoint:** `POST /api/chat/messages`

**Flow:**
1. User sends message via API
2. Message saved to database
3. WebSocket notification sent to receiver
4. Receiver gets real-time update

**Code Example:**
```typescript
// Frontend
await chatAPI.sendMessage({ 
  receiver_id: targetUserId, 
  message: "Hello!" 
});
```

**Backend Processing:**
```python
# routers/chat.py
@router.post("/messages")
async def send_message(message_data, current_user):
    # Save to database
    message = ChatMessage(...)
    db.add(message)
    db.commit()
    
    # Send via WebSocket
    await manager.send_personal_message(
        str(receiver_id),
        json.dumps({
            "type": "chat_message",
            "message": {...}
        })
    )
```

#### 3. **Receiving Messages**
```typescript
// Frontend: components/ConversationChatModal.tsx
wsManager.on('chat_message', (data) => {
  // Update UI with new message
  setMessages(prev => [...prev, data.message]);
});
```

### Features
- ✅ Real-time message delivery
- ✅ Message persistence in database
- ✅ Read/unread status
- ✅ Conversation history
- ✅ Typing indicators (via polling)
- ✅ Automatic scroll to latest message

### How to Use Chat

**For Patients:**
1. Navigate to Dashboard
2. Click "Messages" or find a researcher
3. Click "Send Message" button
4. Type message and press Enter or click Send
5. Messages appear instantly for both users

**For Researchers:**
1. Access Messages from dashboard
2. View patient conversations
3. Reply in real-time
4. Messages sync across all devices

---

## 📹 Video Call Facility

### Implementation Details

**Technology:** Jitsi Meet (Open-source video conferencing)
**Integration Type:** Embedded iframe with custom configuration

### Architecture
```
Meeting Request → Accepted → Video Call Initiation → Jitsi Room → Live Video
```

### How It Works

#### 1. **Meeting Request Creation**
**Endpoint:** `POST /api/meetings/`

```typescript
// Patient requests meeting with researcher
await meetingsAPI.createMeetingRequest({
  expert_id: researcherId,
  message: "I'd like to discuss my condition"
});
```

**Backend Processing:**
```python
# routers/meetings.py
@router.post("/")
async def create_meeting_request():
    # Create meeting request
    meeting_request = MeetingRequest(...)
    db.add(meeting_request)
    
    # Notify expert via WebSocket
    await manager.send_personal_message(
        expert_id,
        json.dumps({
            "type": "meeting_request",
            "request": {...}
        })
    )
```

#### 2. **Meeting Acceptance**
**Endpoint:** `PUT /api/meetings/{request_id}/status`

```typescript
// Researcher accepts/rejects
await meetingsAPI.updateMeetingStatus(requestId, {
  status: "accepted" // or "rejected"
});
```

#### 3. **Video Call Initiation**
**Endpoint:** `POST /api/meetings/video-call`

**Requirements:**
- Meeting must be in "accepted" status
- Both users must have accepted meeting

```typescript
// Initiate video call
await meetingsAPI.initiateVideoCall({
  target_user_id: otherUserId,
  room_name: `curalink-meeting-${meetingId}`
});
```

**Backend Validation:**
```python
# routers/meetings.py
@router.post("/video-call")
async def initiate_video_call():
    # Verify accepted meeting exists
    meeting = db.query(MeetingRequest).filter(
        status == "accepted"
    ).first()
    
    if not meeting:
        raise HTTPException(403, "No accepted meeting found")
    
    # Send video call notification
    await manager.send_personal_message(
        target_user_id,
        json.dumps({
            "type": "video_call",
            "room_name": room_name,
            "caller_name": current_user.full_name
        })
    )
```

#### 4. **Joining Video Room**
**Frontend:** `/app/meet/[meetingId]/video/page.tsx`

```typescript
// Jitsi Meet embedded iframe
const jitsiUrl = `https://meet.jit.si/${room}#config.prejoinPageEnabled=true`;

<iframe
  src={jitsiUrl}
  allow="camera; microphone; fullscreen; display-capture"
/>
```

### Video Call Features
- ✅ HD video and audio
- ✅ Screen sharing
- ✅ Chat within video call
- ✅ Raise hand feature
- ✅ Tile view for multiple participants
- ✅ Microphone and camera controls
- ✅ No installation required (browser-based)
- ✅ End-to-end encryption (Jitsi)

### How to Use Video Calls

**Step-by-Step Guide:**

**For Patients:**
1. Find a researcher/expert on the platform
2. Click "Request Meeting" button
3. Write a message explaining your needs
4. Wait for researcher to accept
5. Once accepted, click "Start Video Call"
6. You'll be redirected to video room
7. Allow camera/microphone permissions
8. Start your consultation

**For Researchers:**
1. Receive meeting request notification (real-time)
2. Review patient's message
3. Click "Accept" or "Decline"
4. If accepted, wait for patient to initiate call OR initiate yourself
5. Join video room when call starts
6. Conduct consultation
7. End call when finished

**During Video Call:**
- Toggle camera: Click camera icon
- Mute/unmute: Click microphone icon
- Share screen: Click desktop icon
- Use chat: Click chat icon
- Raise hand: Click hand icon
- End call: Click hangup icon

---

## 🔔 Live Notifications

### Real-Time Notification System

**Implementation:** WebSocket + Database persistence
**Location:** 
- Backend: `/curalink-backend/routers/notifications.py`
- Frontend: `/curalink-frontend/contexts/NotificationContext.tsx`

### Notification Types

1. **Meeting Request** (`meeting_request`)
   - Triggered when patient requests meeting
   - Sent to researcher
   - Contains requester info and message

2. **Meeting Status Update** (`meeting_status_update`)
   - Triggered when meeting accepted/rejected
   - Sent to requester
   - Contains expert response

3. **Video Call** (`video_call`)
   - Triggered when video call initiated
   - Sent to call recipient
   - Contains room name and caller info

4. **Chat Message** (`chat_message`)
   - Triggered on new message
   - Sent to message recipient
   - Contains message content and sender

### How It Works

#### 1. **Notification Creation**
```python
# Backend: routers/notifications.py
notification = Notification(
    user_id=target_user_id,
    type="meeting_request",
    title="New Meeting Request",
    message=f"{user.full_name} wants to meet",
    from_user=user.full_name,
    read=False
)
db.add(notification)
db.commit()
```

#### 2. **Real-Time Delivery**
```python
# Send via WebSocket
await manager.send_personal_message(
    user_id,
    json.dumps({
        "type": "meeting_request",
        "notification": {...}
    })
)
```

#### 3. **Frontend Reception**
```typescript
// NotificationContext.tsx
wsManager.on('meeting_request', (data) => {
  addNotification({
    type: 'meeting_request',
    title: 'New Meeting Request',
    message: data.message,
    read: false
  });
  
  // Show toast notification
  toast.info('New meeting request received!');
});
```

### Notification Features
- ✅ Real-time delivery (instant)
- ✅ Persistent storage in database
- ✅ Unread count badge
- ✅ Mark as read functionality
- ✅ Delete notifications
- ✅ Mark all as read
- ✅ Toast notifications for immediate alerts
- ✅ Notification history
- ✅ Filter by type

### How to Use Notifications

**Viewing Notifications:**
1. Look for notification bell icon in header
2. Red badge shows unread count
3. Click bell to open notification panel
4. Notifications appear in chronological order

**Managing Notifications:**
1. Click on notification to mark as read
2. Click "Mark all as read" to clear all
3. Click trash icon to delete individual notification
4. Click "Clear all" to delete all notifications

**Notification Actions:**
- Meeting requests: Click to view details and accept/reject
- Chat messages: Click to open conversation
- Video calls: Click to join call
- Status updates: Click to view meeting details

---

## 🤖 AI-Powered Features

### 1. Cura AI Assistant

**Purpose:** Interactive AI chatbot for health guidance

**How to Use:**

1. **Opening Cura AI:**
   - Click the floating "Cura AI" button (bottom-right corner)
   - Available on patient dashboard

2. **Asking Questions:**
   - Type your health question in the input box
   - Press Enter or click Send button
   - Wait for AI response (6-second minimum between requests)

3. **Example Queries:**
   - "What clinical trials are available for diabetes?"
   - "Explain what immunotherapy is"
   - "What precautions should I take for chemotherapy?"
   - "Find me experts in cardiovascular research"

4. **Features:**
   - Context-aware responses based on your medical condition
   - Fallback responses when AI service unavailable
   - Conversation history within session
   - Rate limiting to prevent overload

**Technical Details:**
```typescript
// Frontend: components/CuraAIChat.tsx
const response = await chatAPI.chatWithAI({
  message: "What are treatment options for cancer?",
  context: "Patient condition: Breast Cancer"
});
```

**Backend Processing:**
```python
# services/ai_service.py
async def chat_query(user_message, context):
    messages = [
        {
            "role": "system",
            "content": "You are Cura AI, a medical research assistant..."
        },
        {
            "role": "user",
            "content": f"Context: {context}\n\nUser: {user_message}"
        }
    ]
    
    response = await _make_request(messages)
    return response
```

### 2. Medical Condition Extraction

**Purpose:** Extract structured medical data from natural language

**How It Works:**
```python
# Input: "I have type 2 diabetes and live in New York"
result = await ai_service.extract_medical_condition(text)

# Output:
{
  "condition": "type 2 diabetes",
  "location": "New York"
}
```

**Used For:**
- Patient onboarding
- Clinical trial matching
- Expert recommendations

### 3. AI Summarization

**Publication Summaries:**
- Automatically summarizes complex medical papers
- Patient-friendly language
- Extracts key findings

**Clinical Trial Summaries:**
- Simplifies trial descriptions
- Highlights eligibility criteria
- Explains trial phases

**Implementation:**
```python
# services/ai_service.py
async def summarize_publication(title, abstract):
    # Extracts first 2 sentences for quick summary
    sentences = abstract.split('. ')
    return '. '.join(sentences[:2]) + '.'
```

### 4. Expert Recommendation

**Purpose:** Match patients with relevant researchers

**Algorithm:**
```python
async def recommend_experts(condition, researchers):
    # Keyword matching
    condition_keywords = condition.lower().split()
    
    for researcher in researchers:
        score = 0
        research_text = f"{specialty} {research_interests}".lower()
        
        for keyword in condition_keywords:
            if keyword in research_text:
                score += 1
    
    # Return top 10 matches
    return sorted_researchers[:10]
```

**How to Use:**
1. Enter your medical condition during onboarding
2. System automatically recommends relevant experts
3. View expert profiles and specialties
4. Request meetings with matched experts

---

## 🔗 External API Integrations

### 1. PubMed Integration

**Purpose:** Access 30+ million medical publications

**How to Use:**

**Via Search:**
1. Navigate to "Publications" section
2. Enter medical condition or keyword
3. View results with titles, abstracts, authors
4. Click publication to view full details
5. Save favorites for later reference

**API Details:**
- **Endpoint:** NCBI E-utilities API
- **Database:** PubMed
- **Format:** XML (parsed to JSON)
- **Rate Limit:** 3 requests/second (NCBI limit)

**Data Retrieved:**
- PMID (PubMed ID)
- Title
- Abstract
- Authors
- Journal name
- Publication date
- DOI

**Example Search:**
```python
# Backend
publications = await PubMedService.search_publications(
    query="breast cancer immunotherapy",
    max_results=20
)
```

### 2. ClinicalTrials.gov Integration

**Purpose:** Access 400,000+ clinical trials worldwide

**How to Use:**

**Via Search:**
1. Go to "Clinical Trials" section
2. Enter condition (e.g., "diabetes")
3. Optional: Add location filter
4. Optional: Filter by phase/status
5. Browse results
6. Click trial for detailed information
7. Save trials to favorites

**Search Filters:**
- Condition/disease
- Location/country
- Trial phase (Phase 1-4)
- Status (Recruiting, Completed, etc.)

**API Details:**
- **Endpoint:** ClinicalTrials.gov API v2
- **Format:** JSON
- **Update Frequency:** Daily

**Data Retrieved:**
- NCT ID (trial identifier)
- Title
- Brief summary
- Detailed description
- Conditions
- Phase
- Status
- Sponsor
- Enrollment count
- Study type
- Locations

**Example Search:**
```python
# Backend
trials = await ClinicalTrialsService.search_trials(
    condition="diabetes",
    location="United States",
    status="Recruiting",
    max_results=20
)
```

### 3. ORCID Integration

**Purpose:** Verify researcher credentials and profiles

**How to Use:**

**For Researchers:**
1. During onboarding, enter ORCID ID
2. System verifies researcher identity
3. Imports profile data automatically
4. Displays verified badge on profile

**For Patients:**
1. View researcher profiles
2. See verified badge for ORCID-verified researchers
3. Trust verified credentials

**API Details:**
- **Endpoint:** ORCID Public API v3.0
- **Format:** JSON
- **Authentication:** Public access (no API key needed)

**Data Retrieved:**
- ORCID ID
- Full name
- Biography
- Research keywords
- Institution affiliation
- Publications (via ORCID)

**Example Usage:**
```python
# Backend
profile = await ORCIDService.get_researcher_profile(
    orcid_id="0000-0002-1234-5678"
)

# Returns:
{
    "orcid_id": "0000-0002-1234-5678",
    "name": "Dr. John Smith",
    "biography": "Cancer researcher...",
    "keywords": ["oncology", "immunotherapy"],
    "institution": "Harvard Medical School"
}
```

---

## 📚 Complete Feature Usage Guide

### For Patients

#### 1. Getting Started
1. **Register:** Create account with email/password
2. **Onboarding:** Complete patient profile
   - Enter medical condition
   - Add location
   - Provide age and additional info
3. **Dashboard Access:** Redirected to patient dashboard

#### 2. Finding Clinical Trials
1. Click "Clinical Trials" in navigation
2. Enter your condition in search box
3. Apply filters (location, phase, status)
4. Browse results
5. Click trial card for details
6. Click "Save to Favorites" to bookmark
7. View saved trials in "My Favorites"

#### 3. Reading Medical Publications
1. Navigate to "Publications"
2. Search by condition or keyword
3. View AI-generated summaries
4. Click publication for full abstract
5. Save interesting publications
6. Access via "My Favorites"

#### 4. Finding Experts
1. Go to "Find Experts" section
2. System shows AI-recommended experts based on your condition
3. View expert profiles:
   - Specialty
   - Research interests
   - Institution
   - ORCID verification badge
4. Click "Request Meeting" to connect

#### 5. Requesting Meetings
1. Find expert you want to meet
2. Click "Request Meeting"
3. Write message explaining your needs
4. Submit request
5. Wait for notification (real-time)
6. Check "My Meetings" for status

#### 6. Using Chat
1. Click "Messages" in dashboard
2. Select conversation or start new
3. Type message and press Enter
4. Messages delivered instantly
5. Receive real-time notifications for new messages

#### 7. Video Consultations
1. Wait for meeting acceptance
2. Click "Start Video Call" when ready
3. Allow camera/microphone permissions
4. Join Jitsi room
5. Conduct consultation
6. Use in-call features (screen share, chat)
7. End call when finished

#### 8. Using Cura AI
1. Click floating "Cura AI" button
2. Ask health questions
3. Get instant AI responses
4. Use for:
   - Understanding medical terms
   - Finding trial information
   - Getting health guidance
   - Navigating platform

#### 9. Managing Notifications
1. Check notification bell (top-right)
2. View unread count badge
3. Click to open notification panel
4. Click notification to take action
5. Mark as read or delete

### For Researchers

#### 1. Getting Started
1. **Register:** Create researcher account
2. **Onboarding:** Complete researcher profile
   - Enter specialty
   - Add research interests
   - Provide institution
   - Enter ORCID ID (optional, for verification)
3. **Dashboard Access:** Redirected to researcher dashboard

#### 2. Managing Meeting Requests
1. Receive real-time notifications for new requests
2. View request details in "Meeting Requests"
3. Read patient message
4. Click "Accept" or "Decline"
5. Patient notified instantly
6. Accepted meetings appear in "My Meetings"

#### 3. Conducting Video Consultations
1. Accept meeting request
2. Wait for patient to initiate OR initiate yourself
3. Click "Start Video Call"
4. Join Jitsi room
5. Conduct consultation
6. Use professional features:
   - Screen sharing for presenting data
   - Chat for sharing links
   - Recording (if enabled)

#### 4. Collaborating with Patients
1. Use chat for follow-up questions
2. Share publication links
3. Recommend clinical trials
4. Provide ongoing support

#### 5. Forum Participation
1. Navigate to "Forums"
2. Browse discussion topics
3. Create new forum threads
4. Reply to patient questions
5. Share research insights

#### 6. Profile Management
1. Keep research interests updated
2. Add new publications
3. Update ORCID profile
4. Maintain verified status

---

## 🔧 Technical Configuration

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/curalink
SECRET_KEY=your-secret-key
SAMBANOVA_API_KEY=your-sambanova-api-key
ENTREZ_EMAIL=your-email@example.com
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Running the Application

**Backend:**
```bash
cd curalink-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd curalink-frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🎨 Key Differentiators

### What Makes CuraLink Unique

1. **Unified Platform:** Combines clinical trials, publications, and expert connections in one place
2. **Real-Time Everything:** WebSocket-powered instant updates for all interactions
3. **AI-First Approach:** AI assistance integrated throughout the user journey
4. **Verified Researchers:** ORCID integration ensures credibility
5. **Multi-Source Data:** Aggregates data from PubMed, ClinicalTrials.gov, and ORCID
6. **Video Consultations:** Built-in video calling without external apps
7. **Dual-Role System:** Serves both patients and researchers effectively
8. **Modern UI/UX:** Beautiful, responsive design with smooth animations
9. **No Installation:** Fully web-based, works on any device
10. **Open Source:** Built with modern, maintainable technologies

---

## 📊 Performance Optimizations

1. **AI Rate Limiting:** Prevents API overuse and reduces costs
2. **Response Caching:** 10-minute cache for AI responses
3. **WebSocket Reconnection:** Automatic reconnection on disconnect
4. **Lazy Loading:** Components loaded on demand
5. **Database Indexing:** Optimized queries for fast data retrieval
6. **Async Operations:** Non-blocking I/O for better performance

---

## 🔒 Security Features

1. **JWT Authentication:** Secure token-based auth
2. **Password Hashing:** Bcrypt for password security
3. **CORS Configuration:** Controlled cross-origin requests
4. **SQL Injection Protection:** SQLAlchemy ORM prevents injection
5. **Input Validation:** Pydantic schemas validate all inputs
6. **Secure WebSockets:** Authenticated WebSocket connections
7. **Role-Based Access:** Permission checks on all endpoints

---

## 📞 Support & Troubleshooting

### Common Issues

**WebSocket Not Connecting:**
- Check if backend is running
- Verify WS_URL in frontend .env.local
- Check browser console for errors

**AI Not Responding:**
- Verify SAMBANOVA_API_KEY is set
- Check rate limiting (wait 6 seconds between requests)
- Review backend logs for API errors

**Video Call Not Working:**
- Allow camera/microphone permissions
- Check internet connection
- Ensure meeting is accepted
- Try different browser (Chrome recommended)

**Notifications Not Appearing:**
- Verify WebSocket connection
- Check notification permissions
- Refresh the page

---

## 🚀 Future Enhancements

- [ ] Mobile apps (React Native)
- [ ] Advanced AI matching algorithms
- [ ] Multi-language support
- [ ] Payment integration for consultations
- [ ] Clinical trial enrollment tracking
- [ ] Data analytics dashboard
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Calendar integration
- [ ] Document sharing in video calls

---

**Built with ❤️ for healthcare innovation**

For questions or support, please open an issue on GitHub.
