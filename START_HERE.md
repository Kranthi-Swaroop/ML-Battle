# 🚀 Quick Start Guide - MLBattle

Follow these steps to get MLBattle running on your local machine.

## 📋 Prerequisites Check

Before starting, make sure you have installed:
- ✅ Python 3.10+ 
- ✅ Node.js 18+
- ✅ MongoDB 6.0+
- ✅ Redis Server

---

## 🔧 Step-by-Step Startup

### Step 1: Setup Database (MongoDB)

1. **Start MongoDB** (if not running):
```powershell
# On Windows, MongoDB usually runs as a service
# Check if running:
Get-Service MongoDB

# Or start manually:
net start MongoDB

# Or if installed without service, run:
mongod --dbpath "C:\data\db"
```

2. **Create Database** (optional - MongoDB creates it automatically):
```powershell
# Connect to MongoDB shell
mongosh

# Switch to mlbattle database (creates it if doesn't exist)
use mlbattle

# Optional: Create user for production (development doesn't need auth)
db.createUser({
  user: "mlbattle_user",
  pwd: "mlbattle123",
  roles: [{role: "readWrite", db: "mlbattle"}]
})

exit
```

> **Note:** MongoDB automatically creates the database when you first write to it, so this step is optional for development.

### Step 2: Setup Redis

**Start Redis Server**:
```powershell
# If you have Redis installed on Windows:
redis-server

# Or use WSL:
wsl redis-server

# Or use Docker:
docker run -d -p 6379:6379 redis:latest

# Test Redis is running:
redis-cli ping
# Should return: PONG
```

### Step 3: Setup Backend

```powershell
# Navigate to backend directory
cd d:\MLBattle\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
Copy-Item .env.example .env

# Edit .env file with your settings
notepad .env
```

**Update `.env` with these values:**
```env
DEBUG=True
SECRET_KEY=your-secret-key-for-development
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=mlbattle
MONGO_HOST=localhost
MONGO_PORT=27017
# MONGO_USER=mlbattle_user  # Optional - only for production
# MONGO_PASSWORD=mlbattle123  # Optional - only for production

REDIS_HOST=localhost
REDIS_PORT=6379

CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Optional: Add your Kaggle credentials if you want Kaggle integration
# KAGGLE_USERNAME=your_kaggle_username
# KAGGLE_KEY=your_kaggle_api_key
```

**Run migrations:**
```powershell
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser
# Enter username, email, and password when prompted

# Create static files directory
python manage.py collectstatic --noinput
```

### Step 4: Setup Frontend

**Open a NEW terminal** (keep backend terminal open):
```powershell
# Navigate to frontend directory
cd d:\MLBattle\frontend

# Install dependencies
npm install

# Create .env file
Copy-Item .env.example .env

# Edit .env
notepad .env
```

**Update frontend `.env`:**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8001
```

---

## ▶️ Starting the Application

You'll need **5 terminal windows** open:

### Terminal 1: Django Server
```powershell
cd d:\MLBattle\backend
.\venv\Scripts\activate
python manage.py runserver
```
✅ Django API will run at: **http://localhost:8000**

### Terminal 2: Daphne (WebSocket Server)
```powershell
cd d:\MLBattle\backend
.\venv\Scripts\activate
daphne -p 8001 config.asgi:application
```
✅ WebSocket server will run at: **ws://localhost:8001**

### Terminal 3: Celery Worker
```powershell
cd d:\MLBattle\backend
.\venv\Scripts\activate
celery -A config worker -l info --pool=solo
```
✅ Background tasks will be processed

> **Note:** On Windows, use `--pool=solo` flag for Celery

### Terminal 4: Celery Beat (Scheduler)
```powershell
cd d:\MLBattle\backend
.\venv\Scripts\activate
celery -A config beat -l info
```
✅ Scheduled tasks (Kaggle sync every 5 min) will run

### Terminal 5: React Frontend
```powershell
cd d:\MLBattle\frontend
npm start
```
✅ Frontend will run at: **http://localhost:3000**

---

## 🌐 Access the Application

Once all services are running:

1. **Frontend:** http://localhost:3000
2. **Backend API:** http://localhost:8000/api/
3. **Admin Panel:** http://localhost:8000/admin
4. **API Docs:** http://localhost:8000/api/competitions/

---

## ✅ Verify Everything Works

### Test 1: Check Backend API
```powershell
# In a new terminal or browser
curl http://localhost:8000/api/competitions/
```
Should return JSON response (may be empty list initially)

### Test 2: Check WebSocket
Open browser console at http://localhost:3000 and check for WebSocket connections (no errors)

### Test 3: Register a User
1. Go to http://localhost:3000
2. Click "Register"
3. Fill in the form and create an account
4. You should be redirected to competitions page

### Test 4: Admin Panel
1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. You can create competitions, view users, etc.

---

## 🎯 Quick Start Commands (All in One)

**Option 1: Start Everything Manually (Recommended for first time)**

Use the 5 terminals above.

**Option 2: Create Start Scripts**

Create `start-backend.ps1`:
```powershell
# Start all backend services
cd d:\MLBattle\backend
.\venv\Scripts\activate

# Start Django in background
Start-Process powershell -ArgumentList "-Command cd d:\MLBattle\backend; .\venv\Scripts\activate; python manage.py runserver"

# Start Daphne in background
Start-Process powershell -ArgumentList "-Command cd d:\MLBattle\backend; .\venv\Scripts\activate; daphne -p 8001 config.asgi:application"

# Start Celery Worker
Start-Process powershell -ArgumentList "-Command cd d:\MLBattle\backend; .\venv\Scripts\activate; celery -A config worker -l info --pool=solo"

# Start Celery Beat
Start-Process powershell -ArgumentList "-Command cd d:\MLBattle\backend; .\venv\Scripts\activate; celery -A config beat -l info"

Write-Host "All backend services started!"
```

Create `start-frontend.ps1`:
```powershell
cd d:\MLBattle\frontend
npm start
```

---

## 🐛 Troubleshooting

### Problem: "Module not found" errors
**Solution:**
```powershell
# Backend
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Problem: Database connection error
**Solution:**
- Make sure MongoDB is running: `Get-Service MongoDB`
- Check connection parameters in `.env` file
- Test connection: `mongosh --host localhost --port 27017`
- Verify MongoDB is listening: `netstat -ano | findstr :27017`

### Problem: Redis connection error
**Solution:**
```powershell
# Test if Redis is running
redis-cli ping

# If not, start Redis server
redis-server
# Or use Docker: docker run -d -p 6379:6379 redis
```

### Problem: Port already in use
**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID_NUMBER> /F
```

### Problem: Celery won't start on Windows
**Solution:** Use the `--pool=solo` flag:
```powershell
celery -A config worker -l info --pool=solo
```

### Problem: WebSocket connection fails
**Solution:**
- Make sure Daphne is running on port 8001
- Check frontend .env has correct WS_URL
- Check browser console for connection errors

---

## 📊 What to Do Next

1. **Create Sample Data:**
   - Go to admin panel (http://localhost:8000/admin)
   - Add some competitions manually
   - Set dates and Kaggle competition IDs

2. **Test Features:**
   - Register a new user
   - Browse competitions
   - View leaderboards (will be empty until Kaggle sync runs)
   - Check your profile

3. **Configure Kaggle Integration:**
   - Get Kaggle API credentials from https://www.kaggle.com/account
   - Add them to backend `.env` file
   - Celery Beat will automatically sync leaderboards every 5 minutes

---

## 🎉 You're Ready!

All services should now be running. You can:
- ✅ Access the frontend at http://localhost:3000
- ✅ Register and login
- ✅ Browse competitions
- ✅ View real-time leaderboards
- ✅ Manage data via admin panel

**Need help?** Check:
- `SETUP_GUIDE.md` - Detailed setup instructions
- `PROJECT_COMPLETE.md` - Full feature list
- `DOCUMENTATION_INDEX.md` - All documentation

---

## 🛑 Stopping the Application

To stop all services:
1. Press `Ctrl+C` in each terminal window
2. Deactivate virtual environment: `deactivate`
3. Stop Redis if you started it manually

---

**Happy coding! 🚀**
