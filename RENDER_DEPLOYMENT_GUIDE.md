# 🚀 Complete Render Deployment Guide for CuraLink Backend

## 📋 Prerequisites
- ✅ Backend code pushed to GitHub: https://github.com/karthik24751/CURA-AI
- ✅ Frontend deployed on Vercel: https://curalink-frontend-jca0g93t9-karthik24751s-projects.vercel.app
- ✅ Render account created

---

## 🗄️ STEP 1: Create PostgreSQL Database on Render

### 1.1 Create Database
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Fill in details:
   ```
   Name: curalink-database
   Database: curalink_db
   User: curalink_user
   Region: Singapore (or closest to you)
   PostgreSQL Version: 16
   Plan: Free (or Starter $7/month for production)
   ```
4. Click **"Create Database"**
5. Wait 2-3 minutes for database to be ready

### 1.2 Copy Database URLs
After creation, you'll see:
- **Internal Database URL**: `postgresql://curalink_user:xxxxx@dpg-xxxxx/curalink_db`
- **External Database URL**: `postgresql://curalink_user:xxxxx@dpg-xxxxx-a.singapore-postgres.render.com/curalink_db`

**SAVE BOTH URLs!** You'll need them.

---

## 🧪 STEP 2: Test Database Locally (OPTIONAL but RECOMMENDED)

### 2.1 Run Test Script
```bash
cd /Users/srinivasarao/Desktop/AI\ PROJECT/curalink-backend

# Set the External Database URL
export DATABASE_URL="paste_your_external_database_url_here"

# Run test script
python test-render-db.py
```

### 2.2 Expected Output
```
🔍 Testing database connection...
✅ Connected to PostgreSQL!
📊 Version: PostgreSQL 16.x
🔨 Creating database tables...
✅ All tables created successfully!
📋 Created 11 tables:
   - chat_messages
   - clinical_trials
   - favorites
   - forum_posts
   - forums
   - meeting_requests
   - notifications
   - patient_profiles
   - researcher_profiles
   - users
✅ Database is ready for deployment!
```

If you see this, your database is working perfectly! ✅

---

## 🌐 STEP 3: Deploy Backend to Render

### 3.1 Create Web Service
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository:
   - Click **"Connect account"** (if not connected)
   - Select repository: `karthik24751/CURA-AI`
   - Click **"Connect"**

### 3.2 Configure Web Service
Fill in these details:

**Basic Settings:**
```
Name: curalink-backend
Region: Singapore (same as database)
Branch: main
Root Directory: curalink-backend
Runtime: Python 3
```

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3.3 Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Paste your **Internal Database URL** from Step 1.2 |
| `JWT_SECRET` | `your-super-secret-jwt-key-change-this-in-production` |
| `SAMBANOVA_API_KEY` | Your SambaNova API key |
| `PUBMED_API_KEY` | Your PubMed API key (optional) |
| `PYTHON_VERSION` | `3.9.18` |

**IMPORTANT**: Use the **Internal Database URL** (not External) for production!

### 3.4 Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Watch the logs for any errors

### 3.5 Verify Deployment
Once deployed, you'll get a URL like:
```
https://curalink-backend.onrender.com
```

Test it:
```bash
curl https://curalink-backend.onrender.com/
```

Expected response:
```json
{"message": "CuraLink API is running", "version": "1.0.0"}
```

---

## 🔗 STEP 4: Connect Frontend to Backend

### 4.1 Update Frontend Environment Variables

1. Go to Vercel Dashboard: https://vercel.com/karthik24751s-projects/curalink-frontend
2. Click **"Settings"** → **"Environment Variables"**
3. Add/Update these variables:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://curalink-backend.onrender.com` |
| `NEXT_PUBLIC_WS_URL` | `wss://curalink-backend.onrender.com` |

4. Click **"Save"**

### 4.2 Redeploy Frontend
1. Go to **"Deployments"** tab
2. Click on the latest deployment
3. Click **"Redeploy"**
4. Wait 2-3 minutes

---

## ✅ STEP 5: Test Everything

### 5.1 Test Backend Endpoints
```bash
# Health check
curl https://curalink-backend.onrender.com/

# Test registration
curl -X POST https://curalink-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User",
    "role": "patient"
  }'
```

### 5.2 Test Frontend
1. Open: https://curalink-frontend-jca0g93t9-karthik24751s-projects.vercel.app
2. Try to register a new account
3. Login with the account
4. Test features:
   - ✅ Dashboard loads
   - ✅ Notifications work
   - ✅ Meeting requests work
   - ✅ Real-time updates work
   - ✅ Video calls work
   - ✅ Chat works

---

## 🔧 Troubleshooting

### Issue 1: Database Connection Error
**Error**: `could not connect to server`

**Solution**:
- Check if you used **Internal Database URL** (not External)
- Verify database is in same region as web service
- Check database status in Render dashboard

### Issue 2: Frontend Can't Connect to Backend
**Error**: `Network Error` or `CORS Error`

**Solution**:
1. Check backend URL in Vercel environment variables
2. Verify CORS settings in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://curalink-frontend-jca0g93t9-karthik24751s-projects.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: WebSocket Not Working
**Error**: WebSocket connection failed

**Solution**:
- Render Free tier may have WebSocket limitations
- Consider upgrading to Starter plan ($7/month)
- Check WebSocket URL uses `wss://` (not `ws://`)

### Issue 4: Slow Response Times
**Issue**: Backend responds slowly

**Solution**:
- Render Free tier spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Upgrade to Starter plan for always-on service

---

## 📊 Monitoring

### Check Backend Logs
1. Go to Render Dashboard
2. Click on `curalink-backend`
3. Click **"Logs"** tab
4. Monitor for errors

### Check Database
1. Go to Render Dashboard
2. Click on `curalink-database`
3. Click **"Metrics"** to see usage

---

## 🎉 Success Checklist

- [ ] Database created and tested locally
- [ ] Backend deployed to Render
- [ ] Backend health check passes
- [ ] Frontend environment variables updated
- [ ] Frontend redeployed
- [ ] User registration works
- [ ] Login works
- [ ] Dashboard loads
- [ ] Notifications work in real-time
- [ ] Meeting requests work
- [ ] Video calls work
- [ ] Chat works
- [ ] All features are real-time

---

## 📝 Important URLs

**Frontend (Vercel)**: https://curalink-frontend-jca0g93t9-karthik24751s-projects.vercel.app

**Backend (Render)**: https://curalink-backend.onrender.com (will be available after deployment)

**Database**: Internal URL only (don't share publicly)

**GitHub**: https://github.com/karthik24751/CURA-AI

---

## 🚨 Security Notes

1. **Never commit** `.env` files to GitHub
2. **Change JWT_SECRET** to a random string in production
3. **Use HTTPS** only (both Vercel and Render provide this)
4. **Rotate API keys** regularly
5. **Monitor logs** for suspicious activity

---

## 💰 Cost Breakdown

**Free Tier:**
- Render PostgreSQL: Free (500MB storage, 90 days)
- Render Web Service: Free (750 hours/month, spins down)
- Vercel: Free (unlimited bandwidth)
- **Total: $0/month**

**Production Tier:**
- Render PostgreSQL: $7/month (1GB storage, always-on)
- Render Web Service: $7/month (always-on, no spin-down)
- Vercel: Free (or Pro $20/month for team features)
- **Total: $14-34/month**

---

## 🎯 Next Steps After Deployment

1. Set up custom domain (optional)
2. Configure email notifications (SendGrid/Mailgun)
3. Set up monitoring (Sentry/LogRocket)
4. Add analytics (Google Analytics/Mixpanel)
5. Set up CI/CD for automatic deployments
6. Add automated tests
7. Set up backup strategy for database

---

**Need Help?** Check Render docs: https://render.com/docs
