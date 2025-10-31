# MLBattle - Quick Start Guide

## 🎯 What's Been Built

### ✅ Backend (100% Complete)

All backend functionality has been implemented:

1. **Django Project Structure**
   - Config files (settings, celery, asgi, wsgi, urls)
   - 5 Django apps (users, competitions, submissions, leaderboard, ratings)

2. **Database Models**
   - Custom User model with ELO ratings
   - Competition model with status tracking
   - Submission model
   - LeaderboardEntry model
   - RatingHistory model

3. **REST API**
   - JWT authentication
   - User management endpoints
   - Competition CRUD endpoints
   - Leaderboard endpoints
   - Submission endpoints
   - Rating history endpoints

4. **Kaggle Integration**
   - KaggleService class
   - Automatic leaderboard fetching
   - Background tasks with Celery

5. **ELO Rating System**
   - Dynamic K-factor calculation
   - Rating calculation after competition ends
   - Rating history tracking

6. **Real-time Updates**
   - Django Channels configured
   - WebSocket support for leaderboard
   - Celery Beat for scheduled tasks

### ✅ Frontend (Infrastructure 100% Complete)

All frontend infrastructure and services have been implemented:

1. **Project Setup**
   - package.json with dependencies
   - Environment configuration
   - Folder structure

2. **Services Layer**
   - ✅ api.js - Complete Axios HTTP client with interceptors
   - ✅ websocket.js - WebSocket connection manager
   - ✅ auth.js - Authentication utilities

3. **Custom Hooks**
   - ✅ useAuth.js - Authentication state management
   - ✅ useWebSocket.js - WebSocket connection hook
   - ✅ useLeaderboard.js - Leaderboard with real-time updates

4. **Utilities**
   - ✅ constants.js - App constants and rating tiers
   - ✅ helpers.js - Helper functions for formatting

### 🚧 Frontend (UI Components to Build)

The following components need to be created (examples provided in frontend/README.md):

**Components (src/components/):**
- [ ] Navbar.jsx + Navbar.css
- [ ] Footer.jsx + Footer.css
- [ ] CompetitionCard.jsx + CompetitionCard.css
- [ ] Leaderboard.jsx + Leaderboard.css
- [ ] RatingChart.jsx + RatingChart.css
- [ ] SubmissionHistory.jsx + SubmissionHistory.css

**Pages (src/pages/):**
- [ ] Home.jsx + Home.css
- [ ] CompetitionList.jsx + CompetitionList.css
- [ ] CompetitionDetail.jsx + CompetitionDetail.css
- [ ] Profile.jsx + Profile.css
- [ ] Login.jsx + Login.css
- [ ] Register.jsx + Register.css

**Main Files:**
- [ ] App.jsx - Main component with routing
- [ ] index.js - Entry point
- [ ] App.css - Global styles
- [ ] index.css - Base styles

## 🚀 How to Run the Project

### Step 1: Install Prerequisites

**Windows (PowerShell):**
```powershell
# Install Python 3.10+ from python.org
# Install Node.js 16+ from nodejs.org
# Install MongoDB 6.0+ from mongodb.com/try/download/community
# Install Redis from https://github.com/microsoftarchive/redis/releases
```

### Step 2: Setup Backend

```powershell
# Navigate to backend
cd d:\MLBattle\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
notepad .env

# Start MongoDB (if not running as service)
net start MongoDB

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 3: Start Backend Services

Open **4 separate PowerShell terminals** in the backend directory:

**Terminal 1 - Django Server:**
```powershell
cd d:\MLBattle\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```
✅ Should see: "Starting development server at http://127.0.0.1:8000/"

**Terminal 2 - Celery Worker:**
```powershell
cd d:\MLBattle\backend
.\venv\Scripts\Activate.ps1
celery -A config worker -l info --pool=solo
```
✅ Should see: "celery@... ready"

**Terminal 3 - Celery Beat:**
```powershell
cd d:\MLBattle\backend
.\venv\Scripts\Activate.ps1
celery -A config beat -l info
```
✅ Should see: "beat: Starting..."

**Terminal 4 - Redis Server:**
```powershell
redis-server
```
✅ Should see: "Ready to accept connections"

### Step 4: Setup Frontend

```powershell
# Navigate to frontend
cd d:\MLBattle\frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm start
```
✅ Browser should open at http://localhost:3000

### Step 5: Verify Backend is Working

**Test API Endpoints:**
```powershell
# Open browser and visit:
http://localhost:8000/admin/          # Django admin
http://localhost:8000/api/competitions/    # API endpoint
```

**Test WebSocket:**
```javascript
// Open browser console at http://localhost:3000
const ws = new WebSocket('ws://localhost:8000/ws/leaderboard/1/');
ws.onmessage = (e) => console.log(e.data);
```

## 📝 Next Steps for Development

### Option 1: Build Frontend UI (Recommended)

Follow the examples in `frontend/README.md` to create:

1. **Start with App.jsx:**
   - Set up React Router
   - Add AuthProvider wrapper
   - Create route structure

2. **Create Navbar component:**
   - Use useAuth hook for user state
   - Add navigation links
   - Add logout functionality

3. **Create Login/Register pages:**
   - Use authAPI from services
   - Form validation
   - Redirect on success

4. **Create CompetitionList page:**
   - Use competitionsAPI to fetch data
   - Display CompetitionCard components
   - Add filters

5. **Create CompetitionDetail page:**
   - Use useLeaderboard hook
   - Display live leaderboard
   - Show WebSocket connection status

6. **Create Profile page:**
   - Use usersAPI to fetch data
   - Display RatingChart component
   - Show SubmissionHistory

### Option 2: Test Backend Functionality

**Create a competition via Django Admin:**
1. Visit http://localhost:8000/admin/
2. Add a Competition with a valid Kaggle competition ID
3. Set start/end dates
4. Watch Celery logs to see automatic sync

**Test Kaggle Integration:**
```python
# In Django shell
python manage.py shell

from apps.submissions.kaggle_service import get_kaggle_service
service = get_kaggle_service()
data = service.get_competition_leaderboard('titanic')
print(data)
```

**Test ELO Calculator:**
```python
from apps.ratings.elo_calculator import EloRatingSystem

participants = [
    {'user_id': 1, 'username': 'user1', 'old_rating': 1500, 'rank': 1},
    {'user_id': 2, 'username': 'user2', 'old_rating': 1500, 'rank': 2},
]

results = EloRatingSystem.calculate_competition_ratings(participants)
print(results)
```

## 🔍 Troubleshooting

### Backend Issues

**Django won't start:**
```powershell
# Check if virtual environment is activated
# Ensure all dependencies installed
pip install -r requirements.txt
```

**Database errors:**
```powershell
# Reset migrations (development only!)
python manage.py migrate --fake-initial
```

**Celery not running:**
```powershell
# Windows requires --pool=solo flag
celery -A config worker -l info --pool=solo
```

**Redis connection error:**
```powershell
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### Frontend Issues

**npm install fails:**
```powershell
# Clear cache and retry
npm cache clean --force
npm install
```

**WebSocket connection fails:**
- Check that Django Channels is running
- Verify ASGI application is configured
- Check Redis is running

**API calls return 401:**
- Check JWT tokens in localStorage
- Try logging in again
- Check CORS settings in backend

## 📚 Documentation

- **Backend API:** See `backend/README.md`
- **Frontend Guide:** See `frontend/README.md`
- **This Guide:** `SETUP_GUIDE.md`
- **Main README:** `README.md`

## 🎓 Learning Resources

**Django REST Framework:**
- https://www.django-rest-framework.org/

**Django Channels:**
- https://channels.readthedocs.io/

**React Hooks:**
- https://react.dev/reference/react

**Celery:**
- https://docs.celeryq.dev/

**Kaggle API:**
- https://github.com/Kaggle/kaggle-api

## ✅ Current Status Summary

| Component | Status | Details |
|-----------|--------|---------|
| Backend Models | ✅ Complete | All 5 models implemented |
| Backend API | ✅ Complete | All endpoints working |
| Kaggle Integration | ✅ Complete | Service class ready |
| ELO Rating System | ✅ Complete | Algorithm implemented |
| Celery Tasks | ✅ Complete | Background jobs configured |
| WebSocket Support | ✅ Complete | Django Channels ready |
| Frontend Services | ✅ Complete | API, WebSocket, Auth |
| Frontend Hooks | ✅ Complete | useAuth, useWebSocket, useLeaderboard |
| Frontend UI | 🚧 To Build | Components and pages needed |
| Documentation | ✅ Complete | All READMEs written |

## 🎉 Success!

You now have a fully functional MLBattle backend with:
- ✅ Complete REST API
- ✅ Kaggle integration
- ✅ Real-time WebSocket support
- ✅ ELO rating system
- ✅ Background task processing
- ✅ Frontend infrastructure

**Next:** Build the frontend UI components using the examples provided in `frontend/README.md`.

The heavy lifting is done - now it's time to create the user interface! 🚀
