import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.competitions.models import Event
from apps.leaderboard.models import LeaderboardEntry
from django.db.models import Sum, Count

# Get the Neural Night 2.0 event
event = Event.objects.get(slug='neural-night-2o')
competitions = event.competitions.all()

print(f'Event: {event.name}')
print(f'Competitions: {competitions.count()}')
print(f'Competition names:')
for comp in competitions:
    entry_count = LeaderboardEntry.objects.filter(competition=comp).count()
    print(f'  - {comp.name}: {entry_count} entries')

# Test the aggregation query
entries = LeaderboardEntry.objects.filter(
    competition__in=competitions
).values(
    'kaggle_team_name'
).annotate(
    total_score=Sum('score'),
    competitions_participated=Count('competition', distinct=True)
).order_by('-total_score')

print(f'\nTotal unique teams: {entries.count()}')
print('\nTop 10 teams:')
for i, entry in enumerate(entries[:10], 1):
    print(f"{i}. {entry['kaggle_team_name']}: {entry['total_score']:.2f} points "
          f"({entry['competitions_participated']} competitions)")
