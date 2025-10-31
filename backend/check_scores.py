import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.competitions.models import CompetitionEvent, Competition
from apps.leaderboard.models import LeaderboardEntry

# Get Neural Night 2.0 event
event = CompetitionEvent.objects.get(slug='neural-night-2o')
competitions = event.competitions.all()

print(f"Event: {event.title}")
print(f"Total competitions: {competitions.count()}\n")

# Check scoring configuration for each competition
for comp in competitions:
    print(f"\n{'='*60}")
    print(f"Competition: {comp.title}")
    print(f"  Higher is better: {comp.higher_is_better}")
    print(f"  Min value: {comp.metric_min_value}")
    print(f"  Max value: {comp.metric_max_value}")
    print(f"  Points for perfect score: {comp.points_for_perfect_score}")
    
    # Get sample entries
    entries = LeaderboardEntry.objects.filter(competition=comp).order_by('rank')[:3]
    print(f"  Sample entries (top 3):")
    for entry in entries:
        print(f"    Rank {entry.rank}: {entry.kaggle_team_name} - Score: {entry.score}")

# Check a specific team's scores across competitions
print(f"\n{'='*60}")
print("Team 'nan' scores across all competitions:")
nan_entries = LeaderboardEntry.objects.filter(
    kaggle_team_name='nan',
    competition__in=competitions
).select_related('competition')

for entry in nan_entries:
    print(f"  {entry.competition.title}: Score = {entry.score}, Rank = {entry.rank}")

total = sum(e.score for e in nan_entries)
print(f"\n  Total score: {total}")
print(f"  Competitions participated: {nan_entries.count()} / {competitions.count()}")
