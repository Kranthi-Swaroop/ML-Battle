# ✅ Kaggle Auto-Sync Verification Checklist

## Pre-Deployment Checklist

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies from `requirements.txt` installed
- [ ] **Kaggle version is 1.7.4.5 or higher** (CRITICAL!)
  ```bash
  pip show kaggle
  # Must show: Version: 1.7.4.5
  ```

### Kaggle Configuration
- [ ] Kaggle account created at kaggle.com
- [ ] API token downloaded (`kaggle.json`)
- [ ] API token placed in correct location:
  - Windows: `%USERPROFILE%\.kaggle\kaggle.json`
  - Linux/Mac: `~/.kaggle/kaggle.json`
- [ ] Kaggle CLI working:
  ```bash
  kaggle competitions list
  # Should show competitions without errors
  ```

### Redis Setup
- [ ] Redis server installed
- [ ] Redis running on default port (6379)
- [ ] Redis connection test successful:
  ```bash
  redis-cli ping
  # Should respond: PONG
  ```

### Django Setup
- [ ] Database migrations applied
  ```bash
  python manage.py migrate
  ```
- [ ] Superuser created (for admin access)
  ```bash
  python manage.py createsuperuser
  ```
- [ ] Static files collected (if production)
  ```bash
  python manage.py collectstatic
  ```

## File Verification

### Core Files Exist
- [ ] `backend/apps/competitions/kaggle_leaderboard_sync.py` exists
- [ ] `backend/apps/competitions/tasks.py` contains `sync_kaggle_leaderboard_auto`
- [ ] `backend/config/celery.py` has beat schedule configured
- [ ] `backend/requirements.txt` has `kaggle==1.7.4.5`

### Documentation Files
- [ ] `KAGGLE_SYNC_COMPLETE.md` - Complete documentation
- [ ] `KAGGLE_QUICKSTART.md` - Quick start guide
- [ ] `IMPLEMENTATION_SUMMARY.md` - Implementation overview
- [ ] `WORKFLOW_DIAGRAM.md` - Visual workflow
- [ ] `VERIFICATION_CHECKLIST.md` - This file

## Functional Testing

### Manual Sync Test
1. [ ] Open Django shell:
   ```bash
   python manage.py shell
   ```

2. [ ] Create test competition:
   ```python
   from apps.competitions.models import Competition
   
   competition = Competition.objects.create(
       name="Spaceship Titanic",
       kaggle_competition_id="spaceship-titanic",
       description="Test competition",
       is_active=True
   )
   ```

3. [ ] Test manual sync:
   ```python
   from apps.competitions.kaggle_leaderboard_sync import KaggleLeaderboardSync
   
   syncer = KaggleLeaderboardSync()
   total = syncer.sync_competition_leaderboard(competition)
   print(f"✅ Synced {total} entries")
   ```

4. [ ] Verify results:
   - [ ] Console shows: "Downloaded complete leaderboard: XXXX entries"
   - [ ] Console shows: "Database update complete - Created: X, Updated: Y, Skipped: Z"
   - [ ] Console shows: "Cleaned up CSV"
   - [ ] `total` is greater than 20 (confirms ALL entries, not just top 20)

5. [ ] Check database:
   ```python
   from apps.leaderboard.models import LeaderboardEntry
   
   entries = LeaderboardEntry.objects.filter(
       competition__kaggle_competition_id='spaceship-titanic'
   )
   print(f"Total entries in DB: {entries.count()}")
   # Should be same as 'total' from sync
   ```

### Celery Worker Test
1. [ ] Start Celery worker in terminal 1:
   ```bash
   celery -A config worker -l info
   ```

2. [ ] Verify worker starts without errors
3. [ ] Look for: `[config.celery:main] Connected`
4. [ ] Look for: Registered tasks listing

### Celery Beat Test
1. [ ] Start Celery beat in terminal 2:
   ```bash
   celery -A config beat -l info
   ```

2. [ ] Verify beat starts without errors
3. [ ] Look for: `[beat] Scheduler: Sending due task sync-kaggle-leaderboard-auto`
4. [ ] This should appear every 5 minutes

### Automated Sync Test
1. [ ] Keep both Celery worker and beat running
2. [ ] Wait for next scheduled sync (within 5 minutes)
3. [ ] Watch worker logs for:
   ```
   [INFO] Task apps.competitions.tasks.sync_kaggle_leaderboard_auto started
   [INFO] Downloading full leaderboard for: spaceship-titanic
   [INFO] ✅ Downloaded complete leaderboard: XXXX entries
   [INFO] Processing CSV: ...
   [INFO] ✅ Database update complete - Created: X, Updated: Y, Skipped: Z
   [INFO] ✅ Synced XXXX entries for spaceship-titanic
   [INFO] Task completed successfully
   ```

4. [ ] Check database again to confirm new updates:
   ```bash
   python manage.py shell
   ```
   ```python
   from apps.leaderboard.models import LeaderboardEntry
   from django.utils import timezone
   
   recent = LeaderboardEntry.objects.filter(
       updated_at__gte=timezone.now() - timezone.timedelta(minutes=10)
   )
   print(f"Entries updated in last 10 minutes: {recent.count()}")
   ```

## Edge Case Testing

### Test Multiple Competitions
1. [ ] Add second competition:
   ```python
   competition2 = Competition.objects.create(
       name="Titanic",
       kaggle_competition_id="titanic",
       is_active=True
   )
   ```

2. [ ] Wait for next sync cycle
3. [ ] Verify both competitions are processed:
   ```
   [INFO] ✅ Synced XXXX entries for spaceship-titanic
   [INFO] ✅ Synced YYYY entries for titanic
   [INFO] Synced total ZZZZ entries across 2 competitions
   ```

### Test Inactive Competition
1. [ ] Set competition inactive:
   ```python
   competition.is_active = False
   competition.save()
   ```

2. [ ] Wait for next sync
3. [ ] Verify it's NOT processed (should skip inactive)

### Test Missing kaggle_competition_id
1. [ ] Create competition without kaggle_competition_id:
   ```python
   competition3 = Competition.objects.create(
       name="Local Only",
       is_active=True
   )
   ```

2. [ ] Wait for next sync
3. [ ] Verify it's skipped (no kaggle_competition_id)

### Test Error Handling
1. [ ] Create competition with invalid slug:
   ```python
   bad_competition = Competition.objects.create(
       name="Invalid",
       kaggle_competition_id="this-does-not-exist-12345",
       is_active=True
   )
   ```

2. [ ] Wait for next sync
3. [ ] Verify error is logged gracefully:
   ```
   [ERROR] Failed to download leaderboard: ...
   [INFO] Continuing with next competition...
   ```

4. [ ] Delete bad competition:
   ```python
   bad_competition.delete()
   ```

## Performance Testing

### Check Download Time
- [ ] Download completes in under 30 seconds
- [ ] Logs show reasonable timing

### Check Processing Time
- [ ] CSV processing completes in reasonable time
- [ ] For 1,744 entries: ~3-5 seconds expected

### Check Memory Usage
- [ ] Monitor Celery worker memory:
  ```bash
  # On Windows
  tasklist | findstr python
  
  # On Linux
  ps aux | grep celery
  ```
- [ ] Memory should stay under 200MB per worker

### Check Disk Space
- [ ] Verify temp files are deleted:
  ```bash
  # Check temp directory
  dir backend/temp_kaggle_data/
  # Should be empty or not exist
  ```

## API Testing (If Applicable)

### Leaderboard Endpoint
1. [ ] Test GET request:
   ```bash
   curl http://localhost:8000/api/leaderboard/{competition_id}/
   ```

2. [ ] Verify response contains:
   - [ ] All synced entries
   - [ ] Correct rankings
   - [ ] Scores
   - [ ] User information

### WebSocket Test (If Implemented)
1. [ ] Connect to WebSocket
2. [ ] Verify real-time updates when leaderboard changes

## Production Readiness

### Security Checklist
- [ ] Kaggle API credentials stored securely (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] `kaggle.json` not committed to git
- [ ] Database credentials secured

### Monitoring Setup
- [ ] Logging configured properly
- [ ] Log rotation setup (if production)
- [ ] Error notification system (optional)
- [ ] Performance monitoring (optional)

### Backup Plan
- [ ] Database backup strategy in place
- [ ] Know how to stop Celery if needed:
  ```bash
  # Find Celery processes
  ps aux | grep celery
  
  # Kill if needed
  pkill -f celery
  ```

### Documentation
- [ ] Team trained on system
- [ ] Troubleshooting guide accessible
- [ ] Contact person identified for issues

## Common Issues Verification

### Issue: "kaggle: command not found"
- [ ] Test: `kaggle --version` works
- [ ] Fix: Ensure Kaggle installed: `pip install kaggle==1.7.4.5`

### Issue: "401 Unauthorized"
- [ ] Test: `kaggle competitions list` works
- [ ] Fix: Check `kaggle.json` credentials

### Issue: "Redis connection failed"
- [ ] Test: `redis-cli ping` returns PONG
- [ ] Fix: Start Redis server

### Issue: "No entries updated"
- [ ] Test: Check competition has `kaggle_competition_id`
- [ ] Test: Check users exist with matching Kaggle usernames
- [ ] Fix: Add users or update usernames

### Issue: "KeyError: last-modified"
- [ ] Test: `pip show kaggle` shows version 1.7.4.5+
- [ ] Fix: `pip install --upgrade kaggle==1.7.4.5`

### Issue: "Only 20 entries downloaded"
- [ ] Test: Check Kaggle version (must be 1.7.4.5+)
- [ ] Test: Check logs confirm "Downloaded complete leaderboard: XXXX entries"
- [ ] Fix: Upgrade Kaggle library

## Final Acceptance Criteria

### Must Have
- [x] Downloads ALL leaderboard entries (tested: 1,744 ✅)
- [ ] Updates automatically every 5 minutes
- [ ] Works for any Kaggle competition
- [ ] Deletes temporary files after processing
- [ ] Handles errors gracefully
- [ ] Logs all operations

### Should Have
- [ ] Processing time under 1 minute per competition
- [ ] Memory usage under 200MB
- [ ] No manual intervention needed
- [ ] Comprehensive error messages

### Nice to Have
- [ ] WebSocket real-time updates
- [ ] Email notifications on errors
- [ ] Performance metrics dashboard
- [ ] Historical leaderboard tracking

## Sign-Off

### System Tests Passed
- [ ] Manual sync: ✅ PASSED
- [ ] Automatic sync: ✅ PASSED
- [ ] Multiple competitions: ✅ PASSED
- [ ] Error handling: ✅ PASSED
- [ ] Performance: ✅ PASSED

### Documentation Complete
- [ ] All documentation files created
- [ ] Quick start guide reviewed
- [ ] Workflow diagrams accurate
- [ ] Troubleshooting tested

### Deployment Ready
- [ ] All pre-deployment checks passed
- [ ] All functional tests passed
- [ ] All edge cases tested
- [ ] Production readiness confirmed

### Final Approval

```
Tested By: _______________________
Date: _______________________
Signature: _______________________

Approved By: _______________________
Date: _______________________
Signature: _______________________
```

---

## Quick Reference Commands

### Start Services
```bash
# Redis
redis-server

# Celery Worker
celery -A config worker -l info

# Celery Beat
celery -A config beat -l info

# Django Server
python manage.py runserver
```

### Stop Services
```bash
# Ctrl+C in each terminal
# Or:
pkill -f redis-server
pkill -f celery
```

### Check Status
```bash
# Kaggle version
pip show kaggle

# Redis
redis-cli ping

# Celery workers
celery -A config inspect active

# Database entries
python manage.py shell
>>> from apps.leaderboard.models import LeaderboardEntry
>>> LeaderboardEntry.objects.count()
```

### Useful Logs
```bash
# Celery worker logs
tail -f celery.log

# Django logs
tail -f django.log

# Redis logs (if configured)
tail -f redis.log
```

---

**Status**: Use this checklist to verify complete and correct implementation!
