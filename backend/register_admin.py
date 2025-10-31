"""
Register admin user for a competition
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.users.models import User
from apps.competitions.models import Competition
from apps.leaderboard.models import LeaderboardEntry

# Get admin user
admin = User.objects.filter(username='darkdevil').first()
if not admin:
    print("Admin user not found!")
    exit()

# Get a Kaggle competition
competition = Competition.objects.filter(kaggle_competition_id__isnull=False).exclude(kaggle_competition_id='').first()
if not competition:
    print("No Kaggle competition found!")
    exit()

print(f"Registering {admin.username} for {competition.title}")

# Register user for competition
entry, created = LeaderboardEntry.objects.get_or_create(
    user=admin,
    competition=competition,
    defaults={
        'rank': 0,
        'best_score': 0.0,
        'score': 0.0,
        'submissions_count': 0
    }
)

if created:
    print(f"✅ Successfully registered {admin.username} for {competition.title}")
else:
    print(f"ℹ️  {admin.username} was already registered for {competition.title}")

print(f"\n📊 Total registered users for this competition: {LeaderboardEntry.objects.filter(competition=competition).count()}")
