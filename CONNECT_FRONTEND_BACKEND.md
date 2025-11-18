# 🔗 Connect Vercel Frontend to Render Backend

## 📋 Complete Connection Guide

### **Prerequisites:**
- ✅ Backend deployed on Render
- ✅ Frontend deployed on Vercel
- ✅ Database tables created

---

## 🎯 **Step-by-Step Connection**

### **STEP 1: Get Your Render Backend URL**

After backend deployment completes on Render, you'll see:
```
✅ Live at: https://curalink-backend.onrender.com
```

**Copy this URL!** You'll need it for the next steps.

---

### **STEP 2: Update Vercel Environment Variables**

#### 2.1 Go to Vercel Dashboard
1. Open: https://vercel.com/karthik24751s-projects/curalink-frontend
2. Click on your project name
3. Click **"Settings"** (top menu)
4. Click **"Environment Variables"** (left sidebar)

#### 2.2 Add/Update Variables

**Variable 1: API URL**
```
Key: NEXT_PUBLIC_API_URL
Value: https://curalink-backend.onrender.com
Environments: ✅ Production ✅ Preview ✅ Development
```

**Variable 2: WebSocket URL**
```
Key: NEXT_PUBLIC_WS_URL
Value: wss://curalink-backend.onrender.com
Environments: ✅ Production ✅ Preview ✅ Development
```

**IMPORTANT:**
- Use `https://` for API (not `http://`)
- Use `wss://` for WebSocket (not `ws://`)
- Check ALL three environment boxes

#### 2.3 Save Variables
Click **"Save"** for each variable.

---

### **STEP 3: Redeploy Frontend**

After adding environment variables, you MUST redeploy:

1. Go to **"Deployments"** tab
2. Click on the **latest deployment**
3. Click **"⋯"** (three dots) → **"Redeploy"**
4. Click **"Redeploy"** to confirm
5. Wait 2-3 minutes for redeployment

---

### **STEP 4: Verify Connection**

#### 4.1 Check Backend Health
Open in browser:
```
https://curalink-backend.onrender.com/
```

Expected response:
```json
{
  "message": "CuraLink API is running",
  "version": "1.0.0"
}
```

#### 4.2 Check Frontend Connection
1. Open your Vercel frontend:
   ```
   https://curalink-frontend-jca0g93t9-karthik24751s-projects.vercel.app
   ```

2. Open browser console (F12)

3. Try to register/login

4. Check console for API calls:
   ```
   ✅ POST https://curalink-backend.onrender.com/api/auth/register
   ✅ POST https://curalink-backend.onrender.com/api/auth/login
   ```

---

## 🔧 **Troubleshooting**

### Issue 1: CORS Error
**Error**: `Access to fetch blocked by CORS policy`

**Solution**:
Backend CORS is already configured to allow all origins (`allow_origins=["*"]`).
If you still see this error:
1. Clear browser cache
2. Try incognito/private window
3. Check if backend URL is correct in Vercel env vars

### Issue 2: Network Error
**Error**: `Network Error` or `Failed to fetch`

**Solution**:
1. Verify backend is running:
   ```bash
   curl https://curalink-backend.onrender.com/
   ```
2. Check Render logs for errors
3. Verify environment variables in Vercel are correct
4. Make sure you redeployed frontend after adding env vars

### Issue 3: WebSocket Connection Failed
**Error**: `WebSocket connection to 'wss://...' failed`

**Solution**:
1. Render Free tier may have WebSocket limitations
2. Check if backend is awake (first request after 15 min takes time)
3. Verify `NEXT_PUBLIC_WS_URL` uses `wss://` (not `ws://`)
4. Consider upgrading to Render Starter plan ($7/month)

### Issue 4: 404 Not Found
**Error**: `404 Not Found` on API calls

**Solution**:
1. Check API endpoint paths match:
   - Frontend: `/api/auth/login`
   - Backend: `/api/auth/login`
2. Verify backend routes are included in `main.py`
3. Check Render logs for routing errors

### Issue 5: Slow First Request
**Issue**: First API call takes 30-60 seconds

**Explanation**:
- Render Free tier spins down after 15 minutes of inactivity
- First request "wakes up" the service
- Subsequent requests are fast

**Solutions**:
1. **Free Option**: Accept the delay (only affects first request)
2. **Paid Option**: Upgrade to Starter plan ($7/month) for always-on service
3. **Workaround**: Use a cron job to ping backend every 10 minutes

---

## ✅ **Connection Checklist**

Use this checklist to verify everything is connected:

- [ ] Backend deployed on Render
- [ ] Backend health check returns 200 OK
- [ ] Database tables created (10 tables)
- [ ] `NEXT_PUBLIC_API_URL` added to Vercel
- [ ] `NEXT_PUBLIC_WS_URL` added to Vercel
- [ ] Environment variables applied to all environments
- [ ] Frontend redeployed after adding env vars
- [ ] Can access frontend URL
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Dashboard loads with data
- [ ] Notifications work
- [ ] Meeting requests work
- [ ] WebSocket connection established
- [ ] Real-time updates work

---

## 🧪 **Test Real-Time Features**

### Test 1: User Registration & Login
```bash
# Test registration
curl -X POST https://curalink-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User",
    "role": "patient"
  }'

# Test login
curl -X POST https://curalink-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Test 2: Real-Time Notifications
1. Open frontend in two browser tabs
2. Login as patient in tab 1
3. Login as researcher in tab 2
4. Send meeting request from patient
5. Check if researcher receives instant notification

### Test 3: WebSocket Connection
1. Open browser console (F12)
2. Go to Network tab → WS (WebSocket)
3. Should see connection to `wss://curalink-backend.onrender.com/ws/{user_id}`
4. Status should be "101 Switching Protocols"

---

## 📊 **Environment Variables Summary**

### Vercel Frontend Variables:
```env
NEXT_PUBLIC_API_URL=https://curalink-backend.onrender.com
NEXT_PUBLIC_WS_URL=wss://curalink-backend.onrender.com
```

### Render Backend Variables:
```env
DATABASE_URL=postgresql://root:xxxxx@dpg-xxxxx/curalink_db_xxxxx
JWT_SECRET=curalink-super-secret-jwt-key-2024
SAMBANOVA_API_KEY=your-sambanova-key
PYTHON_VERSION=3.9.18
```

---

## 🎉 **Success Indicators**

When everything is connected correctly, you should see:

✅ **Frontend loads without errors**
✅ **Login/Registration works**
✅ **Dashboard displays data**
✅ **API calls show in Network tab**
✅ **WebSocket connection established**
✅ **Notifications appear instantly**
✅ **Meeting requests work**
✅ **Video calls initiate**
✅ **Chat messages send/receive**
✅ **All features are real-time**

---

## 📝 **Important URLs**

**Frontend (Vercel):**
```
https://curalink-frontend-jca0g93t9-karthik24751s-projects.vercel.app
```

**Backend (Render):**
```
https://curalink-backend.onrender.com
```

**Backend API Docs:**
```
https://curalink-backend.onrender.com/docs
```

**Database:**
```
Internal URL only (configured in Render)
```

---

## 🚨 **Security Notes**

1. ✅ HTTPS enforced on both Vercel and Render
2. ✅ JWT tokens for authentication
3. ✅ CORS configured properly
4. ✅ Database credentials in environment variables (not in code)
5. ✅ WebSocket connections secured with WSS

---

## 💡 **Pro Tips**

1. **Monitor Logs**: Check Render logs regularly for errors
2. **Use Incognito**: Test in incognito mode to avoid cache issues
3. **Check Network Tab**: Browser DevTools → Network tab shows all API calls
4. **Test WebSocket**: Network tab → WS filter shows WebSocket connections
5. **Clear Cache**: If changes don't appear, clear browser cache
6. **Redeploy**: Always redeploy frontend after changing env vars

---

## 🆘 **Need Help?**

If you encounter issues:

1. **Check Render Logs**:
   - Go to Render Dashboard
   - Click on `curalink-backend`
   - Click "Logs" tab

2. **Check Browser Console**:
   - Press F12
   - Look for errors in Console tab
   - Check Network tab for failed requests

3. **Verify Environment Variables**:
   - Vercel: Settings → Environment Variables
   - Render: Dashboard → Environment

4. **Test Backend Directly**:
   ```bash
   curl https://curalink-backend.onrender.com/
   ```

---

**Everything should work perfectly after following these steps!** 🎉
