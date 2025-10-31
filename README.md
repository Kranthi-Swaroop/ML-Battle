# MLBattle - Machine Learning Competition Platform

MLBattle is a comprehensive web-based platform designed to host machine learning competitions with automatic Kaggle integration, real-time leaderboard updates, and an ELO-based rating system.

## 🚀 Features

- **Kaggle Integration** - Automatic fetching of competition results from Kaggle API
- **Real-time Leaderboard** - Live updates via WebSocket connections
- **ELO Rating System** - Track competitive progress with dynamic ratings
- **User Profiles** - View statistics, rating history, and submission history
- **Competition Management** - Browse, filter, and register for competitions
- **Admin Dashboard** - Django admin interface for managing competitions and users

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Django 4.2 + Django REST Framework
- MongoDB (Database with djongo)
- Redis (Cache & Message Broker)
- Celery (Background Tasks)
- Django Channels (WebSockets)
- Kaggle API

**Frontend:**
- React 18.2
- React Router v6
- Axios (HTTP Client)
- Chart.js (Data Visualization)
- Native WebSocket API

## 📋 Prerequisites

- Python 3.10+
- Node.js 16+
- MongoDB 6.0+
- Redis Server
- Kaggle API credentials

## 🛠️ Installation & Setup

### Backend Setup

1. **Navigate to backend directory:**
```powershell
cd backend
```

2. **Create virtual environment:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

4. **Configure environment:**
```powershell
cp .env.example .env
# Edit .env with your configuration
```

5. **Start MongoDB:**
```powershell
# Check if MongoDB is running
Get-Service MongoDB

# Start if not running
net start MongoDB
```

6. **Run migrations:**
```powershell
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser:**
```powershell
python manage.py createsuperuser
```

8. **Start services (5 terminals needed):**

**Terminal 1 - Django:**
```powershell
python manage.py runserver
```

**Terminal 2 - Daphne (WebSocket):**
```powershell
daphne -p 8001 config.asgi:application
```

**Terminal 3 - Celery Worker:**
```powershell
celery -A config worker -l info --pool=solo
```

**Terminal 4 - Celery Beat:**
```powershell
celery -A config beat -l info
```

**Terminal 5 - Redis:**
```powershell
redis-server
```

> **Note:** See **START_HERE.md** for detailed 5-terminal startup guide!

### Frontend Setup

1. **Navigate to frontend directory:**
```powershell
cd frontend
```

2. **Install dependencies:**
```powershell
npm install
```

3. **Configure environment:**
```powershell
cp .env.example .env
# Edit .env if needed
```

4. **Start development server:**
```powershell
npm start
```

The application will open at `http://localhost:3000`

## 📁 Project Structure

```
MLBattle/
├── backend/                          # Django backend
│   ├── config/                       # Project configuration
│   │   ├── settings/                 # Settings modules
│   │   ├── celery.py                 # ✅ Celery config
│   │   ├── asgi.py                   # ✅ ASGI config
│   │   ├── wsgi.py                   # ✅ WSGI config
│   │   └── urls.py                   # ✅ URL routing
│   ├── apps/
│   │   ├── users/                    # ✅ User management
│   │   ├── competitions/             # ✅ Competition CRUD
│   │   ├── submissions/              # ✅ Kaggle integration
│   │   ├── leaderboard/              # ✅ Leaderboard & WebSockets
│   │   └── ratings/                  # ✅ ELO rating system
│   ├── manage.py                     # ✅ Django management
│   ├── requirements.txt              # ✅ Python dependencies
│   ├── .env.example                  # ✅ Example environment
│   └── README.md                     # ✅ Backend documentation
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/               # Reusable components
│   │   ├── pages/                    # Page components
│   │   ├── services/
│   │   │   ├── api.js                # ✅ Axios HTTP client
│   │   │   ├── websocket.js          # ✅ WebSocket manager
│   │   │   └── auth.js               # ✅ Auth utilities
│   │   ├── hooks/
│   │   │   ├── useAuth.js            # ✅ Auth hook
│   │   │   ├── useWebSocket.js       # ✅ WebSocket hook
│   │   │   └── useLeaderboard.js     # ✅ Leaderboard hook
│   │   ├── utils/
│   │   │   ├── constants.js          # ✅ App constants
│   │   │   └── helpers.js            # ✅ Helper functions
│   │   ├── App.jsx                   # Main app component
│   │   └── index.js                  # Entry point
│   ├── package.json                  # ✅ Dependencies
│   ├── .env.example                  # ✅ Example environment
│   └── README.md                     # ✅ Frontend documentation
└── README.md                         # ✅ This file
```

## 🎯 Key Features Implementation Status

### ✅ Completed (Backend)

- [x] Django project structure
- [x] Custom User model with ELO ratings
- [x] Competition model with status management
- [x] Submission tracking
- [x] Leaderboard entries
- [x] Rating history
- [x] REST API endpoints
- [x] JWT authentication
- [x] Kaggle API integration service
- [x] ELO rating calculator
- [x] Celery background tasks
- [x] Celery Beat scheduling
- [x] Django Channels WebSocket support
- [x] Real-time leaderboard updates
- [x] Admin interface configuration

### ✅ Completed (Frontend - Core)

- [x] Project structure
- [x] API service with Axios
- [x] WebSocket manager
- [x] Authentication utilities
- [x] Custom hooks (useAuth, useWebSocket, useLeaderboard)
- [x] Helper functions and constants

### 🚧 To Complete (Frontend - UI)

- [ ] Navbar component
- [ ] Footer component
- [ ] CompetitionCard component
- [ ] Leaderboard component
- [ ] RatingChart component
- [ ] SubmissionHistory component
- [ ] Home page
- [ ] CompetitionList page
- [ ] CompetitionDetail page
- [ ] Profile page
- [ ] Login page
- [ ] Register page
- [ ] App.jsx with routing
- [ ] CSS styling

## 🔄 Workflow

### User Journey

1. User registers/logs in
2. Browses available competitions
3. Registers for a competition
4. Navigates to Kaggle (external link)
5. Downloads dataset and builds ML model
6. Submits predictions on Kaggle
7. Returns to platform to view live leaderboard
8. Tracks rating changes after competition ends

### Backend Data Flow

1. Celery Beat triggers scheduled task (every 5 min)
2. Celery Worker fetches Kaggle leaderboard
3. Updates database with new scores/ranks
4. Sends WebSocket notification
5. Frontend receives real-time update
6. Leaderboard re-renders automatically

### Rating Calculation Flow

1. Competition ends
2. Background task calculates ratings
3. ELO algorithm processes all participants
4. User ratings updated
5. Rating history records created

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/users/register/` - Register

### Competitions
- `GET /api/competitions/` - List competitions
- `GET /api/competitions/{id}/` - Competition details
- `GET /api/competitions/ongoing/` - Ongoing competitions
- `POST /api/competitions/{id}/register/` - Register for competition

### Leaderboard
- `GET /api/leaderboard/?competition={id}` - Competition leaderboard
- `WS /ws/leaderboard/{id}/` - Real-time updates

### Users
- `GET /api/users/me/` - Current user
- `GET /api/users/{id}/rating_history/` - Rating history
- `GET /api/users/{id}/submissions/` - User submissions

## 🧪 Testing

### Backend
```powershell
cd backend
python manage.py test
```

### Frontend
```powershell
cd frontend
npm test
```

## 🚀 Deployment

### Backend (Production)

1. Update settings in `config/settings/production.py`
2. Set environment variables
3. Run migrations
4. Collect static files: `python manage.py collectstatic`
5. Use Gunicorn for WSGI: `gunicorn config.wsgi:application`
6. Use Daphne for ASGI: `daphne config.asgi:application`

### Frontend (Production)

1. Build: `npm run build`
2. Serve static files with Nginx or hosting service

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=mlbattle
MONGO_HOST=localhost
MONGO_PORT=27017
# MONGO_USER=          # Optional for development
# MONGO_PASSWORD=      # Optional for development
REDIS_URL=redis://localhost:6379/0
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend Environment Variables (.env)

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## � Quick Start

**New to the project?** Follow these guides in order:

1. **[START_HERE.md](START_HERE.md)** ⭐ - Complete setup guide with 5-terminal instructions
2. **[MONGODB_SETUP.md](MONGODB_SETUP.md)** - Detailed MongoDB installation guide
3. **[MONGODB_MIGRATION.md](MONGODB_MIGRATION.md)** - Why MongoDB? Migration details
4. **[PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)** - Full feature list

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture diagrams
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - All documentation index
- **[backend/README.md](backend/README.md)** - Backend API documentation
- **[frontend/README.md](frontend/README.md)** - Frontend component examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

MIT License

## 👥 Authors

MLBattle Development Team

## 🙏 Acknowledgments

- Kaggle for competition data API
- Django and React communities
- All contributors and testers

---

**Note:** This project provides a solid foundation with all backend functionality and frontend infrastructure complete. The remaining work involves creating the UI components and pages following the examples in the frontend README.
