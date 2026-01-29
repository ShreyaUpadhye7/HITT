# 🚀 Step-by-Step Deployment Guide

## **Current Status:**
✅ SendGrid API Key: Added to Render  
❌ Python Analysis Service: Not deployed yet  
❌ AI_SERVER_URL: Still pointing to localhost  

---

## **Step 1: Deploy Python Analysis Service**

### **Method 1: Using Render Dashboard (Easiest)**

1. **Go to Render Dashboard**: https://dashboard.render.com/

2. **Create New Service**:
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select your repository from the list

3. **Configure the Service**:
   ```
   Name: hitt-analysis-service
   Root Directory: analysis_service
   Environment: Python 3
   Build Command: pip install -r requirement.txt
   Start Command: python api.py
   Instance Type: Free
   ```

4. **Add Environment Variables**:
   ```
   OCR_SPACE_API_KEY = K86065005788957
   PORT = 5000
   ```

5. **Click "Create Web Service"**

6. **Wait for Deployment** (5-10 minutes)
   - You'll see build logs
   - Once deployed, you'll get a URL like: `https://hitt-analysis-service.onrender.com`

---

## **Step 2: Update Your Main Server**

Once your analysis service is deployed:

1. **Go to your main server service** on Render Dashboard
2. **Click "Environment"** tab
3. **Update AI_SERVER_URL**:
   ```
   AI_SERVER_URL = https://hitt-analysis-service.onrender.com
   ```
4. **Click "Save Changes"**
5. Your server will automatically redeploy

---

## **Step 3: Test Everything**

### **Test Analysis Service**:
Visit: `https://hitt-analysis-service.onrender.com`
You should see: `{"message": "HITT Handwriting Analyzer API is running!"}`

### **Test Registration**:
1. Go to your frontend: https://hitt-eight.vercel.app
2. Try to register with a real email
3. Check your email for OTP
4. Complete registration

### **Test Handwriting Analysis**:
1. Login as a Counselor
2. Register a patient
3. Upload a handwriting sample
4. Check if analysis works

---

## **Troubleshooting**

### **If Analysis Service Fails to Deploy**:
- Check build logs in Render dashboard
- Make sure all model files are in the repository
- Verify `requirement.txt` has all dependencies

### **If Analysis Still Fails**:
- Check if AI_SERVER_URL is correctly updated
- Look at server logs in Render dashboard
- Verify the analysis service is responding

### **If Registration Still Fails**:
- Verify SendGrid API key is correct
- Check if sender email is verified in SendGrid
- Look at server logs for email errors

---

## **Expected URLs After Deployment**:

- **Frontend**: https://hitt-eight.vercel.app
- **Main Server**: https://hitt-1-i3s1.onrender.com  
- **Analysis Service**: https://hitt-analysis-service.onrender.com

---

## **Quick Commands to Check**:

```bash
# Test analysis service
curl https://hitt-analysis-service.onrender.com

# Test main server
curl https://hitt-1-i3s1.onrender.com

# Check if CORS is working
curl -H "Origin: https://hitt-eight.vercel.app" https://hitt-1-i3s1.onrender.com
```

---

## **What Happens Next**:

1. ✅ **Registration**: Users receive OTP emails
2. ✅ **Login**: Authentication works properly
3. ✅ **Analysis**: Handwriting analysis processes images
4. ✅ **All Features**: Dashboard, history, profiles work

Your app will be fully functional! 🎉