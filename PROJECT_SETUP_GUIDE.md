# Project Setup Guide

## Overview
This project is a handwriting analysis application with three main components:
- **Frontend**: React application (Vite + React 19)
- **Backend**: Node.js/Express server with MongoDB
- **Analysis Service**: Python Flask service with TensorFlow/Keras models

## Prerequisites

### 1. System Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **RAM**: Minimum 8GB (16GB recommended for TensorFlow)
- **Storage**: At least 5GB free space

### 2. Required Software

#### Node.js and npm
- **Version**: Node.js 18.x or higher
- **Download**: https://nodejs.org/
- **Verify installation**:
```cmd
node --version
npm --version
```

#### Python
- **Version**: Python 3.8 - 3.11 (TensorFlow compatibility)
- **Download**: https://www.python.org/downloads/
- **Verify installation**:
```cmd
python --version
pip --version
```

#### MongoDB
- **MongoDB Community Server**: https://www.mongodb.com/try/download/community
- **MongoDB Compass** (GUI): https://www.mongodb.com/try/download/compass

#### Git
- **Download**: https://git-scm.com/downloads
- **Verify installation**:
```cmd
git --version
```

## Installation Steps

### 1. Clone the Repository
```cmd
git clone <your-repository-url>
cd <project-directory>
```

### 2. MongoDB Setup

#### Install MongoDB Community Server
1. Download and install MongoDB Community Server
2. Start MongoDB service:
```cmd
# Windows (as Administrator)
net start MongoDB

# macOS/Linux
sudo systemctl start mongod
```

#### Install MongoDB Compass
1. Download and install MongoDB Compass
2. Connect to: `mongodb://localhost:27017`
3. Create a new database for your project

### 3. Backend Server Setup
```cmd
cd server
npm install
```

#### Create Environment File
Create `.env` file in the `server` directory:
```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/your-database-name
JWT_SECRET=your-jwt-secret-key
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone
```

### 4. Frontend Client Setup
```cmd
cd client
npm install
```

### 5. Python Analysis Service Setup

#### Create Virtual Environment
```cmd
cd analysis_service
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### Install Python Dependencies
```cmd
pip install -r requirement.txt
```

#### Additional Python Dependencies (if needed)
```cmd
pip install opencv-python requests
```

#### Create Environment File
Create `.env` file in the `analysis_service` directory:
```env
OCR_SPACE_API_KEY=your-ocr-space-api-key
PORT=5001
```

### 6. Required API Keys

#### OCR.space API Key
1. Visit: https://ocr.space/ocrapi
2. Sign up for a free account
3. Get your API key
4. Add to `analysis_service/.env`

## Running the Application

### 1. Start MongoDB
```cmd
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod
```

### 2. Start Backend Server
```cmd
cd server
npm start
# or for development:
node server.js
```
Server will run on: http://localhost:5000

### 3. Start Analysis Service
```cmd
cd analysis_service
# Activate virtual environment first
venv\Scripts\activate  # Windows

python analyzer.py
```
Analysis service will run on: http://localhost:5001

### 4. Start Frontend Client
```cmd
cd client
npm run dev
```
Client will run on: http://localhost:5173

## Project Structure
```
project/
├── client/                 # React frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── server/                 # Node.js backend
│   ├── server.js
│   ├── package.json
│   └── .env
├── analysis_service/       # Python ML service
│   ├── analyzer.py
│   ├── models/            # TensorFlow models
│   ├── requirement.txt
│   ├── venv/
│   └── .env
└── PROJECT_SETUP_GUIDE.md
```

## MongoDB Compass Configuration

### 1. Connect to Database
- **Connection String**: `mongodb://localhost:27017`
- **Database Name**: Create your project database

### 2. Collections Setup
Create the following collections in MongoDB Compass:
- `users` - User authentication data
- `analyses` - Handwriting analysis results
- `reports` - Generated reports

### 3. Sample Database Connection Test
```javascript
// Test connection in MongoDB Compass
use your-database-name
db.test.insertOne({message: "Connection successful"})
db.test.find()
```

## Troubleshooting

### Common Issues

#### Python TensorFlow Installation
If TensorFlow installation fails:
```cmd
pip install --upgrade pip
pip install tensorflow==2.13.0
```

#### MongoDB Connection Issues
- Ensure MongoDB service is running
- Check firewall settings
- Verify connection string in `.env`

#### Port Conflicts
- Frontend: Change port in `vite.config.js`
- Backend: Change PORT in `server/.env`
- Analysis Service: Change PORT in `analysis_service/.env`

#### Virtual Environment Issues
```cmd
# Recreate virtual environment
cd analysis_service
rmdir /s venv  # Windows
rm -rf venv    # macOS/Linux
python -m venv venv
```

## Development Commands

### Backend Development
```cmd
cd server
npm run dev  # If nodemon is configured
```

### Frontend Development
```cmd
cd client
npm run dev
npm run build     # Production build
npm run preview   # Preview production build
```

### Python Service Development
```cmd
cd analysis_service
python analyzer.py  # Run with debug mode
```

## Production Deployment Notes

### Environment Variables
- Set all API keys and secrets
- Use production MongoDB URI
- Configure CORS for production domains

### Build Commands
```cmd
# Frontend production build
cd client
npm run build

# Backend (no build needed, just ensure dependencies)
cd server
npm install --production
```

## Support
- Ensure all services are running before testing
- Check logs for detailed error messages
- Verify all API keys are correctly configured
- Test MongoDB connection in Compass before running the application