# 🚨 QUICK FIX - Requirements.txt Issue

## **🗑️ STEP 1: DELETE FAILED SERVICES**

Go to Render Dashboard and **DELETE** these services:
- ❌ **HITT** (the Python one that's deploying - keep HITT-1)
- ❌ **hitt-yd-models** (failed build)
- ❌ **hitt-t-models** (failed build)
- ❌ **hitt-pressure** (failed build)

## **✅ STEP 2: KEEP THESE SERVICES**
- ✅ **HITT-1** (Node.js server)
- ✅ **hitt-coordinator** (Python coordinator)

## **📤 STEP 3: PUSH FIXED CODE**
```bash
git add .
git commit -m "Fix requirements.txt path and add render configs"
git push origin main
```

## **🔧 STEP 4: CREATE NEW SERVICES CORRECTLY**

### **Service 1: Pressure & Spacing**
1. **New +** → **Web Service**
2. **Connect GitHub repo**
3. **Settings**:
   - **Name**: `hitt-pressure`
   - **Root Directory**: `analysis_service`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python service_pressure.py`
   - **Environment Variables**:
     ```
     OCR_SPACE_API_KEY = K86065005788957
     PORT = 5000
     ```

### **Service 2: T-Models**
1. **New +** → **Web Service**
2. **Connect GitHub repo**
3. **Settings**:
   - **Name**: `hitt-t-models`
   - **Root Directory**: `analysis_service`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python service_t_models.py`
   - **Environment Variables**:
     ```
     OCR_SPACE_API_KEY = K86065005788957
     PORT = 5000
     ```

### **Service 3: Y&D Models**
1. **New +** → **Web Service**
2. **Connect GitHub repo**
3. **Settings**:
   - **Name**: `hitt-yd-models`
   - **Root Directory**: `analysis_service`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python service_yd_models.py`
   - **Environment Variables**:
     ```
     OCR_SPACE_API_KEY = K86065005788957
     PORT = 5000
     ```

## **🔑 KEY FIX:**
**Root Directory**: `analysis_service` - This tells Render to look for requirements.txt in the right folder!

## **📋 FINAL SERVICES YOU'LL HAVE:**
- ✅ **HITT-1** (Node.js main server)
- ✅ **hitt-coordinator** (Coordinator + G-model)
- ✅ **hitt-pressure** (Pressure & spacing)
- ✅ **hitt-t-models** (T-letter models)
- ✅ **hitt-yd-models** (Y&D letter models)

## **🎯 AFTER ALL SERVICES DEPLOY:**

Update **hitt-coordinator** environment variables:
```
PRESSURE_SERVICE_URL = https://hitt-pressure.onrender.com
T_SERVICE_URL = https://hitt-t-models.onrender.com
YD_SERVICE_URL = https://hitt-yd-models.onrender.com
```

**This will definitely work! The Root Directory fix solves the requirements.txt issue.** 🚀