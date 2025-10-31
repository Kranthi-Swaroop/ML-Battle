# 🚀 Quick Start: Kaggle Leaderboard Auto-Sync

## Prerequisites

1. **Kaggle API Credentials**
   - Go to https://www.kaggle.com/account
   - Click "Create New API Token"
   - Save `kaggle.json` to `~/.kaggle/kaggle.json`

2. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## Setup Steps

### 1. Verify Kaggle Version
```bash
pip show kaggle
# Should be: Version: 1.7.4.5 or higher
```

If not 1.7.4.5+:
```bash
pip install --upgrade kaggle==1.7.4.5
```

### 2. Configure Environment
Create `.env` in backend directory:
```bash
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

### 3. Test Kaggle CLI
```bash
kaggle competitions list
# Should show competitions without errors
```

### 4. Add Competition to Database
```python
python manage.py shell

from apps.competitions.models import Competition

competition = Competition.objects.create(
    name="Spaceship Titanic",
    kaggle_competition_id="spaceship-titanic",  # IMPORTANT: Use exact Kaggle slug
    description="Predict which passengers are transported to an alternate dimension",
    start_date="2025-01-01",
    end_date="2025-12-31",
    is_active=True
)
```

### 5. Test Manual Sync
```python
from apps.competitions.kaggle_leaderboard_sync import KaggleLeaderboardSync
from apps.competitions.models import Competition

syncer = KaggleLeaderboardSync()
competition = Competition.objects.get(kaggle_competition_id='spaceship-titanic')
total = syncer.sync_competition_leaderboard(competition)
print(f"✅ Synced {total} entries")
```

### 6. Start Redis (Required for Celery)
```bash
# Install Redis first if not installed
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Or use Docker:
docker run -d -p 6379:6379 redis
```

### 7. Start Celery Worker
```bash
cd backend
celery -A config worker -l info
```

### 8. Start Celery Beat (Auto-Sync)
```bash
# In another terminal
cd backend
celery -A config beat -l info
```

## Verification

### Check Sync is Working
Watch Celery beat logs for:
```
[INFO/Beat] Scheduler: Sending due task sync-kaggle-leaderboard-auto
```

Watch Celery worker logs for:
```
[INFO] Downloading full leaderboard for: spaceship-titanic
[INFO] ✅ Downloaded complete leaderboard: 1744 entries
[INFO] ✅ Database update complete - Created: X, Updated: Y, Skipped: Z
```

### Check Database
```python
python manage.py shell

from apps.leaderboard.models import LeaderboardEntry

entries = LeaderboardEntry.objects.filter(
    competition__kaggle_competition_id='spaceship-titanic'
).order_by('rank')

print(f"Total entries: {entries.count()}")
print(f"Top entry: {entries.first()}")
```

## Troubleshooting

### Issue: "kaggle: command not found"
**Solution**: Ensure Kaggle is installed in your Python environment
```bash
pip install kaggle==1.7.4.5
```

### Issue: "Could not find kaggle.json"
**Solution**: Place credentials in correct location
```bash
# Windows
mkdir %USERPROFILE%\.kaggle
copy kaggle.json %USERPROFILE%\.kaggle\

# Linux/Mac
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Issue: "401 Unauthorized"
**Solution**: Verify Kaggle credentials are correct
```bash
kaggle competitions list
# Should NOT show authentication errors
```

### Issue: "No entries updated"
**Solution**: Ensure usernames in database match Kaggle usernames exactly

### Issue: Redis Connection Error
**Solution**: Start Redis server
```bash
# Check if Redis is running
redis-cli ping
# Should respond: PONG

# If not running, start it
redis-server
```

## Configuration

### Change Sync Frequency
Edit `backend/config/celery.py`:
```python
app.conf.beat_schedule = {
    'sync-kaggle-leaderboard-auto': {
        'task': 'apps.competitions.tasks.sync_kaggle_leaderboard_auto',
        'schedule': 300.0,  # Change this (in seconds)
    },
}
```

Common intervals:
- Every 1 minute: `60.0`
- Every 5 minutes: `300.0` (default)
- Every 15 minutes: `900.0`
- Every hour: `3600.0`

### Change Temp Directory
Edit `backend/apps/competitions/kaggle_leaderboard_sync.py`:
```python
def __init__(self):
    self.temp_dir = os.path.join(settings.BASE_DIR, 'your_dir_name')
```

## API Endpoints

### View Leaderboard
```bash
GET /api/leaderboard/{competition_id}/
```

### Real-Time Updates (WebSocket)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/leaderboard/');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Leaderboard updated:', data);
};
```

## Production Deployment

### Use Supervisor for Celery
```ini
[program:celery-worker]
command=/path/to/venv/bin/celery -A config worker -l info
directory=/path/to/backend
user=your_user
autostart=true
autorestart=true

[program:celery-beat]
command=/path/to/venv/bin/celery -A config beat -l info
directory=/path/to/backend
user=your_user
autostart=true
autorestart=true
```

### Use systemd (Linux)
```ini
# /etc/systemd/system/celery-worker.service
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=your_user
WorkingDirectory=/path/to/backend
ExecStart=/path/to/venv/bin/celery multi start worker -A config --loglevel=info
ExecStop=/path/to/venv/bin/celery multi stopwait worker
Restart=always

[Install]
WantedBy=multi-user.target
```

## Monitoring

### Check Celery Status
```bash
celery -A config inspect active
celery -A config inspect scheduled
celery -A config inspect stats
```

### View Logs
```bash
tail -f celery.log
```

### Database Metrics
```python
from apps.leaderboard.models import LeaderboardEntry
from django.db.models import Count

# Entries per competition
stats = LeaderboardEntry.objects.values(
    'competition__name'
).annotate(
    total=Count('id')
).order_by('-total')

for stat in stats:
    print(f"{stat['competition__name']}: {stat['total']} entries")
```

## Success Checklist

- [ ] Kaggle 1.7.4.5+ installed
- [ ] Kaggle credentials configured
- [ ] Redis running
- [ ] Competition added to database with `kaggle_competition_id`
- [ ] Manual sync test successful
- [ ] Celery worker running
- [ ] Celery beat running
- [ ] Auto-sync logs show success
- [ ] Database has entries
- [ ] Frontend displays leaderboard

## Next Steps

1. **Add More Competitions**: Just set `kaggle_competition_id` on any competition
2. **Setup Frontend**: Use WebSocket for real-time updates
3. **User Notifications**: Alert users when rank changes
4. **Analytics**: Track leaderboard changes over time
5. **Mobile App**: Consume the API endpoints

---

**Questions?** Check `KAGGLE_SYNC_COMPLETE.md` for detailed documentation.
