import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.leaderboard.models import LeaderboardEntry

entries = LeaderboardEntry.objects.filter(competition_id=20).order_by('rank')
print(f'Total entries for competition 20: {entries.count()}')
print(f'\nFirst 10 entries:')
for e in entries[:10]:
    user_display = e.user.username if e.user else e.kaggle_team_name
    print(f'  Rank {e.rank}: {user_display} - Score: {e.score}')
