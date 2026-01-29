# Deployment Issues Fix Guide

## Issues Identified:

### 1. **Registration/Login Not Working**
- **Problem**: Missing SendGrid API key for email verification
- **Solution**: Add `SENDGRID_API_KEY` to your Render environment variables

### 2. **Handwriting Analysis Failing**
- **Problem**: AI_SERVER_URL pointing to localhost instead of deployed service
- **Solution**: Update AI_SERVER_URL to your deployed analysis service URL

### 3. **CORS Errors**
- **Problem**: CORS not properly configured for production domains
- **Solution**: Updated CORS configuration in server.js

## Step-by-Step Fix:

### Step 1: Update Environment Variables on Render

Go to your Render dashboard → Your server service → Environment tab and add/update:

```
SENDGRID_API_KEY=your_sendgrid_api_key_here
FRONTEND_URL=https://hitt-eight.vercel.app
AI_SERVER_URL=https://your-analysis-service-url.onrender.com
```

### Step 2: Get SendGrid API Key

1. Go to https://sendgrid.com/
2. Sign up/login
3. Go to Settings → API Keys
4. Create a new API key with "Full Access"
5. Add this key to your Render environment variables

### Step 3: Deploy Analysis Service

Your Python analysis service needs to be deployed separately:

1. Create a new Render service for `analysis_service` folder
2. Set build command: `pip install -r requirement.txt`
3. Set start command: `python api.py`
4. Update AI_SERVER_URL with the deployed URL

### Step 4: Update Client Environment

Create a `.env` file in the client folder:

```
VITE_API_URL=https://hitt-1-i3s1.onrender.com
```

### Step 5: Verify Email Configuration

Make sure your SendGrid sender email is verified:
1. Go to SendGrid → Settings → Sender Authentication
2. Verify your sender email (drugalcohol07@gmail.com)

## Common Issues:

### Registration Says "Couldn't Fetch"
- Check if SENDGRID_API_KEY is set correctly
- Verify sender email in SendGrid
- Check server logs for email sending errors

### Handwriting Analysis Fails
- Ensure AI_SERVER_URL points to deployed analysis service
- Check if analysis service is running and accessible
- Verify model files are included in deployment

### CORS Errors
- Make sure your frontend domain is in the CORS origin list
- Check if credentials are being sent properly

## Testing Steps:

1. **Test Registration**: Try registering with a real email
2. **Check Email**: Look for OTP email in inbox/spam
3. **Test Login**: Use registered credentials
4. **Test Analysis**: Upload a handwriting sample

## Deployment URLs to Update:

- **Frontend**: https://hitt-eight.vercel.app
- **Backend**: https://hitt-1-i3s1.onrender.com  
- **Analysis Service**: Deploy separately and update AI_SERVER_URL

## Additional Notes:

- MongoDB Atlas connection is working (good!)
- JWT secret is properly set
- File upload is configured for memory storage (Render compatible)
- All API endpoints are properly defined

The main issue is the missing email service configuration and incorrect service URLs for production deployment.