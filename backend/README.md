# MLBattle Backend

Backend API server for MLBattle - A Machine Learning Competition Platform with Kaggle Integration.

## Technology Stack

- **Django 4.2** - Web framework
- **Django REST Framework** - RESTful API
- **Django Channels** - WebSocket support for real-time updates
- **PostgreSQL** - Primary database
- **Redis** - Caching and message broker
- **Celery** - Background task processing
- **Kaggle API** - Competition data integration

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- Redis Server
- Kaggle API credentials

## Setup Instructions

### 1. Install Python Dependencies

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory:

```powershell
# Copy the example environment file
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=mlbattle
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Kaggle API
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_EXPIRATION_HOURS=24
```

### 3. Setup PostgreSQL Database

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE mlbattle;

# Exit psql
\q
```

### 4. Setup Kaggle API

1. Go to https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New API Token"
4. Save the downloaded `kaggle.json` file
5. Copy credentials to `.env` file

### 5. Run Database Migrations

```powershell
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 6. Create Superuser

```powershell
python manage.py createsuperuser
```

### 7. Start Services

You'll need multiple terminal windows:

**Terminal 1 - Django Development Server:**
```powershell
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```powershell
celery -A config worker -l info --pool=solo
```

**Terminal 3 - Celery Beat (Scheduler):**
```powershell
celery -A config beat -l info
```

**Terminal 4 - Redis Server:**
```powershell
redis-server
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/users/register/` - Register new user

### Users
- `GET /api/users/` - List all users
- `GET /api/users/{id}/` - Get user details
- `GET /api/users/me/` - Get current user profile
- `GET /api/users/{id}/rating_history/` - Get user rating history
- `GET /api/users/{id}/submissions/` - Get user submissions

### Competitions
- `GET /api/competitions/` - List all competitions
- `GET /api/competitions/{id}/` - Get competition details
- `GET /api/competitions/ongoing/` - List ongoing competitions
- `GET /api/competitions/upcoming/` - List upcoming competitions
- `GET /api/competitions/completed/` - List completed competitions
- `GET /api/competitions/{id}/leaderboard/` - Get competition leaderboard
- `POST /api/competitions/{id}/register/` - Register for competition
- `POST /api/competitions/` - Create competition (admin only)

### Leaderboard
- `GET /api/leaderboard/` - List leaderboard entries
- `GET /api/leaderboard/?competition={id}` - Filter by competition
- `GET /api/leaderboard/?user={id}` - Filter by user

### Submissions
- `GET /api/submissions/` - List all submissions
- `GET /api/submissions/{id}/` - Get submission details
- `GET /api/submissions/?user={id}` - Filter by user
- `GET /api/submissions/?competition={id}` - Filter by competition

### Ratings
- `GET /api/ratings/` - List rating history
- `GET /api/ratings/?user={id}` - Filter by user
- `GET /api/ratings/?competition={id}` - Filter by competition

### WebSocket
- `WS /ws/leaderboard/{competition_id}/` - Real-time leaderboard updates

## Project Structure

```
backend/
├── config/                     # Project configuration
│   ├── settings/
│   │   ├── base.py            # Base settings
│   │   ├── local.py           # Development settings
│   │   └── production.py      # Production settings
│   ├── __init__.py
│   ├── asgi.py                # ASGI configuration
│   ├── celery.py              # Celery configuration
│   ├── urls.py                # URL routing
│   └── wsgi.py                # WSGI configuration
├── apps/
│   ├── users/                 # User management
│   ├── competitions/          # Competition CRUD
│   ├── submissions/           # Kaggle integration
│   ├── leaderboard/           # Leaderboard & WebSockets
│   └── ratings/               # ELO rating system
├── manage.py
├── requirements.txt
├── .env                       # Environment variables
├── .env.example              # Example environment file
├── .gitignore
└── README.md
```

## Background Tasks

### Scheduled Tasks (Celery Beat)

1. **Fetch Kaggle Leaderboards** - Every 5 minutes
   - Fetches leaderboard data from Kaggle for all active competitions
   - Updates database with latest scores and ranks
   - Sends real-time updates via WebSocket

2. **Update Competition Status** - Every 10 minutes
   - Updates competition status based on start/end dates
   - Triggers rating calculation when competition ends

### Manual Tasks

- `calculate_ratings_after_competition(competition_id)` - Calculate ELO ratings

## Testing

```powershell
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users
python manage.py test apps.competitions
python manage.py test apps.ratings

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Admin Interface

Access the Django admin interface at: http://localhost:8000/admin

## Common Issues

### Issue: Import errors when running Django
**Solution:** Make sure your virtual environment is activated and all dependencies are installed.

### Issue: Celery tasks not executing
**Solution:** Ensure Redis is running and Celery worker is started with `--pool=solo` on Windows.

### Issue: Kaggle API authentication fails
**Solution:** Verify `KAGGLE_USERNAME` and `KAGGLE_KEY` in `.env` file match your Kaggle API credentials.

### Issue: WebSocket connection fails
**Solution:** Ensure Redis is running and `CHANNEL_LAYERS` is configured correctly in settings.

### Issue: Database connection error
**Solution:** Verify PostgreSQL is running and credentials in `.env` are correct.

## Development Tips

- Use Django shell for quick testing: `python manage.py shell`
- Check Celery task status: `celery -A config inspect active`
- Monitor Redis: `redis-cli monitor`
- View logs in real-time for debugging

## License

MIT License
