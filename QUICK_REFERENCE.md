# 🚀 Kaggle Auto-Sync Quick Reference

## ✨ TL;DR

**Create competition → Auto-sync happens!**

No manual triggers. No extra steps. Just create and go! 🎉

---

## 📋 Quick Examples

### Example 1: Standalone Competition
```python
Competition.objects.create(
    title="My Competition",
    kaggle_competition_id="kaggle-slug",  # Just set this!
    status='ongoing'
)
# ✅ Auto-syncs immediately!
```

### Example 2: Competition in Event
```python
event = CompetitionEvent.objects.create(...)

Competition.objects.create(
    event=event,  # Import in event
    title="Event Competition",
    kaggle_competition_id="spaceship-titanic",
    status='ongoing'
)
# ✅ Auto-syncs immediately!
```

### Example 3: Bulk Import
```python
for kaggle_slug in ['titanic', 'house-prices', 'digit-recognizer']:
    Competition.objects.create(
        kaggle_competition_id=kaggle_slug,
        status='ongoing',
        # ... other fields
    )
# ✅ All 3 auto-sync in parallel!
```

---

## 🎯 When Auto-Sync Triggers

| Action | Auto-Sync? |
|--------|-----------|
| Create with `kaggle_competition_id` + `status='ongoing'` | ✅ YES |
| Create with `status='upcoming'` | ❌ NO (waits) |
| Change status to `'ongoing'` | ✅ YES |
| Update other fields | ❌ NO |
| Add to event | ✅ YES (if ongoing) |

---

## 🔍 Verify It Works

```python
# 1. Create competition
competition = Competition.objects.create(
    kaggle_competition_id="spaceship-titanic",
    status='ongoing',
    # ...
)

# 2. Check Celery logs (within 2 seconds)
# Look for: "🚀 Auto-triggering Kaggle sync"

# 3. Wait 15-20 seconds, check database
from apps.leaderboard.models import LeaderboardEntry
entries = LeaderboardEntry.objects.filter(competition=competition)
print(f"Entries synced: {entries.count()}")
# Should show: 1744+ entries
```

---

## 📊 What Gets Synced

- ✅ ALL leaderboard entries (not just 20)
- ✅ Ranks
- ✅ Scores
- ✅ Submission dates
- ✅ Team info

---

## ⚡ Features

| Feature | Status |
|---------|--------|
| **Automatic trigger** | ✅ |
| **Non-blocking** | ✅ |
| **Background processing** | ✅ |
| **Works in admin** | ✅ |
| **Works in API** | ✅ |
| **Works in code** | ✅ |
| **Bulk import support** | ✅ |
| **Error handling** | ✅ |
| **Logging** | ✅ |
| **Zero config** | ✅ |

---

## 🛠️ Requirements

```bash
# Must be running:
✅ Redis server
✅ Celery worker: celery -A config worker -l info
✅ Celery beat: celery -A config beat -l info

# Must be installed:
✅ kaggle==1.7.4.5
✅ pandas>=2.0.0
✅ protobuf>=6.33.0
```

---

## 📝 Behind the Scenes

```
Create Competition
    ↓
Django Signal Fires
    ↓
Queue Celery Task (immediate)
    ↓
Celery Worker Executes
    ↓
Download from Kaggle
    ↓
Update Database
    ↓
Clean Up Files
    ↓
Done! (15-20 seconds total)
```

---

## 🎓 Common Scenarios

### Import Multiple Competitions in Event
```python
event = CompetitionEvent.objects.create(title="AI Fest")

for kaggle_id in competition_ids:
    Competition.objects.create(
        event=event,
        kaggle_competition_id=kaggle_id,
        status='ongoing'
    )
# All auto-sync in parallel!
```

### Admin Panel
```
1. Click "Add Competition"
2. Fill form
3. Set Kaggle Competition ID
4. Set status to "ongoing"  
5. Click "Save"
→ Auto-sync triggered!
```

### API Endpoint
```bash
POST /api/competitions/
{
  "title": "New Competition",
  "kaggle_competition_id": "titanic",
  "status": "ongoing"
}
→ Auto-sync triggered!
```

---

## 🔧 Troubleshooting

### Sync Not Working?

**Check 1**: Celery running?
```bash
# Should see workers active
celery -A config inspect active
```

**Check 2**: Competition has Kaggle ID?
```python
competition.kaggle_competition_id  # Must not be None/empty
```

**Check 3**: Status is 'ongoing'?
```python
competition.status  # Must be 'ongoing' for new competitions
```

**Check 4**: Celery logs?
```bash
# Look for:
"🚀 Auto-triggering Kaggle sync"
"✅ Sync task queued"
```

---

## 📚 Full Documentation

- **Setup**: `KAGGLE_QUICKSTART.md`
- **How it works**: `AUTO_SYNC_EXPLAINED.md`
- **Complete docs**: `KAGGLE_SYNC_COMPLETE.md`
- **Examples**: `backend/example_auto_sync.py`
- **All docs**: `KAGGLE_DOCUMENTATION_INDEX.md`

---

## ✅ Checklist

Before creating competitions:
- [ ] Redis running
- [ ] Celery worker running
- [ ] Celery beat running
- [ ] Kaggle 1.7.4.5 installed
- [ ] Kaggle credentials configured

When creating competition:
- [ ] Set `kaggle_competition_id`
- [ ] Set `status='ongoing'` (if want immediate sync)
- [ ] Check Celery logs after creation

After creation:
- [ ] Verify logs show sync triggered
- [ ] Wait 15-20 seconds
- [ ] Check LeaderboardEntry count

---

## 🎉 That's It!

**No manual sync needed!**

Just create competitions and the system handles the rest! 🚀

---

**Questions?** See `AUTO_SYNC_EXPLAINED.md` for detailed explanations.
