# 🎯 Automatic Kaggle Sync - How It Works

## ✨ Zero Configuration Required!

When you create or import a competition, the Kaggle leaderboard sync **happens automatically** - no manual triggers needed!

## 🔄 How It Works

### 1. Create/Import Competition

When you create a competition through **any method**:

```python
# Method 1: Direct creation
competition = Competition.objects.create(
    title="Spaceship Titanic",
    kaggle_competition_id="spaceship-titanic",  # Just set this!
    description="Predict passenger transport",
    start_date=timezone.now(),
    end_date=timezone.now() + timedelta(days=30),
    status='ongoing'
)
# ✅ Sync automatically triggers!

# Method 2: Admin panel
# Just fill in the form and save
# ✅ Sync automatically triggers!

# Method 3: API endpoint
# POST to /api/competitions/
# ✅ Sync automatically triggers!

# Method 4: Import in an event
competition_event = CompetitionEvent.objects.get(id=1)
competition = Competition.objects.create(
    event=competition_event,  # Link to event
    title="Titanic ML",
    kaggle_competition_id="titanic",
    status='ongoing',
    # ... other fields
)
# ✅ Sync automatically triggers!
```

### 2. Django Signal Detects It

```python
# Automatically runs when Competition is saved
@receiver(post_save, sender=Competition)
def auto_sync_kaggle_leaderboard(sender, instance, created, **kwargs):
    # Checks if competition has kaggle_competition_id
    # Triggers Celery task immediately
    sync_competition_leaderboard_task.delay(instance.id)
```

### 3. Celery Task Executes Sync

```python
# Runs in background (non-blocking)
@shared_task
def sync_competition_leaderboard_task(competition_id):
    # 1. Download complete leaderboard from Kaggle
    # 2. Update database with all entries
    # 3. Clean up temporary files
    # 4. Log results
```

## 🎬 Complete Flow Diagram

```
User Action
    │
    ├─▶ Create Competition (Admin/API/Code)
    │
    ├─▶ Import Competition in Event
    │
    └─▶ Update Competition Status to 'ongoing'
            │
            ▼
    Django saves Competition
            │
            ▼
    post_save signal fires
            │
            ▼
    Signal checks:
    ✅ Has kaggle_competition_id?
    ✅ Is new OR status='ongoing'?
            │
            ▼
    YES → Queue Celery Task
            │
            ▼
    sync_competition_leaderboard_task.delay()
            │
            ▼
    ┌─────────────────────────┐
    │   Celery Worker Picks   │
    │   Up Task (Background)  │
    └────────────┬────────────┘
                 │
                 ▼
    Download from Kaggle (ALL entries)
                 │
                 ▼
    Update LeaderboardEntry models
                 │
                 ▼
    Delete temporary CSV
                 │
                 ▼
    Log: "✅ Synced 1744 entries"
                 │
                 ▼
    DONE! (User continues working)
```

## ⚡ Sync Triggers

The automatic sync triggers when:

### Trigger 1: New Competition Created
```python
competition = Competition.objects.create(
    kaggle_competition_id="spaceship-titanic",  # Must be set
    # ... other fields
)
# ✅ Immediate sync triggered!
```

### Trigger 2: Competition Becomes Active
```python
competition.status = 'ongoing'
competition.save()
# ✅ Sync triggered!
```

### Trigger 3: Scheduled Auto-Sync (Every 5 Minutes)
```python
# Runs automatically via Celery Beat
# Syncs all active competitions
# No manual intervention needed
```

## 🎯 When Import Happens

### Scenario: Import Competition in Event

```python
# You're creating a competition event
event = CompetitionEvent.objects.create(
    title="Neural Night 2025",
    start_date=timezone.now(),
    end_date=timezone.now() + timedelta(days=7)
)

# Now add competitions to this event
competition1 = Competition.objects.create(
    event=event,  # Link to event
    title="Image Classification Challenge",
    kaggle_competition_id="imagenet-mini",
    status='ongoing',
    start_date=event.start_date,
    end_date=event.end_date
)
# ✅ Auto-sync triggered for competition1!

competition2 = Competition.objects.create(
    event=event,
    title="NLP Sentiment Analysis",
    kaggle_competition_id="sentiment-analysis",
    status='ongoing',
    start_date=event.start_date,
    end_date=event.end_date
)
# ✅ Auto-sync triggered for competition2!

# Result: Both competitions now have full leaderboards!
```

## 🔍 What Gets Synced Automatically?

When sync triggers:
- ✅ **ALL leaderboard entries** (not just top 20)
- ✅ **Ranks** for each participant
- ✅ **Scores** with full precision
- ✅ **Submission dates** and counts
- ✅ **Team information** and usernames

## 📊 Real-World Example

```python
# Admin creates competition via Django Admin
# Fills form:
# - Title: "Spaceship Titanic"
# - Kaggle Competition ID: "spaceship-titanic"
# - Status: "ongoing"
# - Start/End dates
# Clicks "Save"

# Behind the scenes (automatic):
[2025-10-31 22:00:00] INFO: 📝 New Competition Created: Spaceship Titanic
[2025-10-31 22:00:00] INFO: 🚀 Auto-triggering Kaggle sync (New competition created)
[2025-10-31 22:00:00] INFO: ✅ Sync task queued for competition: Spaceship Titanic
[2025-10-31 22:00:05] INFO: Downloading full leaderboard for: spaceship-titanic
[2025-10-31 22:00:12] INFO: ✅ Downloaded complete leaderboard: 1744 entries
[2025-10-31 22:00:15] INFO: ✅ Database update complete - Created: 1744, Updated: 0
[2025-10-31 22:00:15] INFO: ✅ Auto-sync complete for 'Spaceship Titanic': 1744 entries

# Admin can immediately see leaderboard - no waiting!
```

## 🎛️ Signal Configuration

The signals are automatically loaded when Django starts:

**File**: `backend/apps/competitions/apps.py`
```python
class CompetitionsConfig(AppConfig):
    def ready(self):
        import apps.competitions.signals  # Loads signals
```

**File**: `backend/apps/competitions/signals.py`
```python
@receiver(post_save, sender=Competition)
def auto_sync_kaggle_leaderboard(sender, instance, created, **kwargs):
    """Automatically triggered on Competition save"""
    if not instance.kaggle_competition_id:
        return  # Skip if no Kaggle ID
    
    if created or instance.status == 'ongoing':
        # Queue async task
        sync_competition_leaderboard_task.delay(instance.id)
```

## 🚀 Benefits of Auto-Sync

### Before (Manual)
```python
# Create competition
competition = Competition.objects.create(...)

# Manually trigger sync
from apps.competitions.kaggle_leaderboard_sync import KaggleLeaderboardSync
syncer = KaggleLeaderboardSync()
syncer.sync_competition_leaderboard(competition)  # Must remember!
```

### After (Automatic)
```python
# Create competition
competition = Competition.objects.create(...)
# Done! Sync happens automatically in background
```

## ⚙️ Technical Details

### Non-Blocking Execution
- Sync runs in **Celery worker** (background)
- User doesn't wait for completion
- Can create multiple competitions simultaneously
- Each gets its own sync task

### Error Handling
```python
# If sync fails:
# - Error is logged
# - User is not blocked
# - Scheduled sync will retry in 5 minutes
# - Manual retry possible via admin
```

### Avoiding Duplicate Syncs
- Each competition gets **unique task**
- Celery ensures **one task per competition at a time**
- If already syncing, new request is **queued**

## 📝 Logging & Monitoring

Every auto-sync is logged:

```log
[INFO] 📝 New Competition Created:
   Title: Spaceship Titanic
   Kaggle ID: spaceship-titanic
   Status: ongoing
   Event: Neural Night 2025

[INFO] 🚀 Auto-triggering Kaggle sync (New competition created)
[INFO] ✅ Sync task queued for competition: Spaceship Titanic
[INFO] ✅ Auto-sync complete: 1744 entries processed
```

## 🔧 Configuration Options

### Disable Auto-Sync (If Needed)
```python
# In settings.py
ENABLE_AUTO_KAGGLE_SYNC = False  # Default: True

# In signals.py
if not getattr(settings, 'ENABLE_AUTO_KAGGLE_SYNC', True):
    return  # Skip auto-sync
```

### Customize Sync Conditions
```python
# In signals.py
# Only sync for specific statuses
if instance.status in ['ongoing', 'upcoming']:
    sync_competition_leaderboard_task.delay(instance.id)
```

## 🎯 Use Cases

### Use Case 1: Bulk Import
```python
# Import multiple competitions from CSV/API
competitions_data = [
    {'title': 'Comp 1', 'kaggle_id': 'comp-1'},
    {'title': 'Comp 2', 'kaggle_id': 'comp-2'},
    {'title': 'Comp 3', 'kaggle_id': 'comp-3'},
]

for data in competitions_data:
    Competition.objects.create(
        title=data['title'],
        kaggle_competition_id=data['kaggle_id'],
        status='ongoing',
        # ... other fields
    )
    # Each triggers auto-sync independently!

# Result: All 3 competitions sync in parallel
```

### Use Case 2: Event Management
```python
# Create event with multiple competitions
event = CompetitionEvent.objects.create(title="AI Fest 2025")

# Add competitions (each auto-syncs)
for i in range(5):
    Competition.objects.create(
        event=event,
        title=f"Challenge {i+1}",
        kaggle_competition_id=f"challenge-{i+1}",
        status='ongoing'
    )
# All 5 leaderboards sync automatically!
```

### Use Case 3: Admin Panel
```
Admin clicks "Add Competition"
→ Fills form with Kaggle ID
→ Clicks "Save"
→ Redirected to competition list
→ (Background: Sync happening)
→ Refresh page in 15 seconds
→ Full leaderboard visible!
```

## ✅ Verification

After creating a competition, check logs:

```bash
# Watch Celery worker logs
tail -f celery.log

# Look for:
[INFO] 🚀 Auto-triggering Kaggle sync
[INFO] ✅ Auto-sync complete: XXXX entries processed
```

Or check in Django shell:

```python
from apps.leaderboard.models import LeaderboardEntry

# Check if entries were created
entries = LeaderboardEntry.objects.filter(
    competition__kaggle_competition_id='spaceship-titanic'
)
print(f"Total entries: {entries.count()}")
# Should show: Total entries: 1744 (or however many)
```

## 🎉 Summary

**You don't need to do ANYTHING extra!**

Just:
1. ✅ Create competition with `kaggle_competition_id`
2. ✅ Set status to `'ongoing'`
3. ✅ **That's it!**

The system automatically:
- 🚀 Detects the new competition
- 📥 Downloads complete leaderboard
- 💾 Updates database
- 🧹 Cleans up temporary files
- 📝 Logs everything
- ♻️ Repeats every 5 minutes

**Zero manual work required!** 🎯
