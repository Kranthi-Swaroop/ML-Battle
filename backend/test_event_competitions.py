"""
Test script to verify competitions are properly imported into events
and displayed correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

# Disable signals for testing
from django.db.models.signals import post_save
from apps.competitions.models import Competition
from apps.competitions import signals

# Disconnect the auto-sync signal to avoid Redis errors during testing
post_save.disconnect(signals.auto_sync_kaggle_leaderboard, sender=Competition)
post_save.disconnect(signals.log_competition_changes, sender=Competition)

from django.utils import timezone
from datetime import timedelta
from apps.competitions.models import Competition, CompetitionEvent


def test_event_competitions():
    """Test if competitions are properly linked to events and displayed"""
    
    print("\n" + "="*100)
    print("TESTING EVENT COMPETITIONS DISPLAY")
    print("="*100 + "\n")
    
    # Create test event
    event = CompetitionEvent.objects.create(
        title="Test Event - Display Check",
        description="Testing if competitions show up in events",
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=7),
        status='ongoing',
        organizer="Test Team"
    )
    
    print(f"✅ Created Event: {event.title}")
    print(f"   Slug: {event.slug}")
    print(f"   ID: {event.id}\n")
    
    # Create competitions in the event with unique IDs
    import random
    random_suffix = random.randint(1000, 9999)
    competitions_data = [
        {'title': f'Test Competition 1 ({random_suffix})', 'kaggle_id': f'test-comp-1-{random_suffix}'},
        {'title': f'Test Competition 2 ({random_suffix})', 'kaggle_id': f'test-comp-2-{random_suffix}'},
        {'title': f'Test Competition 3 ({random_suffix})', 'kaggle_id': f'test-comp-3-{random_suffix}'},
    ]
    
    created_comps = []
    for comp_data in competitions_data:
        competition = Competition.objects.create(
            event=event,  # Link to event
            title=comp_data['title'],
            description=f"Test competition: {comp_data['kaggle_id']}",
            kaggle_competition_id=comp_data['kaggle_id'],
            kaggle_url=f"https://www.kaggle.com/c/{comp_data['kaggle_id']}",
            start_date=event.start_date,
            end_date=event.end_date,
            status='ongoing',
            rating_weight=1.0,
            max_submissions_per_day=5
        )
        created_comps.append(competition)
        print(f"✅ Created Competition: {competition.title}")
        print(f"   ID: {competition.id}")
        print(f"   Event: {competition.event.title if competition.event else 'None'}")
        print(f"   Kaggle ID: {competition.kaggle_competition_id}")
        print()
    
    # Test retrieval through event
    print("="*100)
    print("TESTING RETRIEVAL")
    print("="*100 + "\n")
    
    # Method 1: Through event.competitions
    event_competitions = event.competitions.all()
    print(f"📊 Event.competitions.all() count: {event_competitions.count()}")
    for comp in event_competitions:
        print(f"   - {comp.title} (ID: {comp.id})")
    
    print()
    
    # Method 2: Through Competition filter
    filtered_comps = Competition.objects.filter(event=event)
    print(f"📊 Competition.objects.filter(event=event) count: {filtered_comps.count()}")
    for comp in filtered_comps:
        print(f"   - {comp.title} (ID: {comp.id})")
    
    print()
    
    # Method 3: Check all competitions (including standalone)
    all_comps = Competition.objects.all()
    print(f"📊 All competitions in database: {all_comps.count()}")
    event_count = all_comps.filter(event__isnull=False).count()
    standalone_count = all_comps.filter(event__isnull=True).count()
    print(f"   - With event: {event_count}")
    print(f"   - Standalone: {standalone_count}")
    
    print()
    
    # Test serializer
    print("="*100)
    print("TESTING SERIALIZER")
    print("="*100 + "\n")
    
    from apps.competitions.serializers import CompetitionListSerializer, CompetitionEventDetailSerializer
    
    serializer = CompetitionEventDetailSerializer(event)
    data = serializer.data
    
    print(f"Event Title: {data['title']}")
    print(f"Competition Count Property: {data.get('competition_count')}")
    print(f"Competitions in serialized data: {len(data.get('competitions', []))}")
    
    if data.get('competitions'):
        print("\nCompetitions from serializer:")
        for comp in data['competitions']:
            print(f"   - {comp['title']} (ID: {comp['id']})")
    else:
        print("\n⚠️  WARNING: No competitions in serialized data!")
    
    print()
    
    # Test API endpoint simulation
    print("="*100)
    print("TESTING API ENDPOINT SIMULATION")
    print("="*100 + "\n")
    
    # Simulate what the view does
    competitions_from_event = event.competitions.all()
    serializer = CompetitionListSerializer(competitions_from_event, many=True)
    api_data = serializer.data
    
    print(f"API endpoint would return: {len(api_data)} competitions")
    for comp in api_data:
        print(f"   - {comp['title']}")
        print(f"     Event: {comp.get('event')}")
        print(f"     Event Title: {comp.get('event_title')}")
        print()
    
    # Final summary
    print("="*100)
    print("SUMMARY")
    print("="*100 + "\n")
    
    if event_competitions.count() == len(created_comps):
        print(f"✅ SUCCESS! All {len(created_comps)} competitions are linked to event")
        print(f"✅ Event.competitions.all() returns correct count")
        
        if len(api_data) == len(created_comps):
            print(f"✅ API serialization works correctly")
        else:
            print(f"❌ API serialization issue: Expected {len(created_comps)}, got {len(api_data)}")
        
        if data.get('competitions') and len(data['competitions']) == len(created_comps):
            print(f"✅ EventDetail serializer includes competitions")
        else:
            print(f"❌ EventDetail serializer issue")
    else:
        print(f"❌ FAILED! Expected {len(created_comps)} competitions, found {event_competitions.count()}")
    
    print()
    
    # Cleanup option
    print("="*100)
    response = input("Delete test data? (y/n): ")
    if response.lower() == 'y':
        event.delete()  # Cascade will delete competitions
        print("✅ Test data deleted")
    else:
        print(f"⚠️  Test data preserved:")
        print(f"   Event ID: {event.id}")
        print(f"   Event Slug: {event.slug}")
        print(f"   URL: /api/competitions/events/{event.slug}/")
        print(f"   Competitions URL: /api/competitions/events/{event.slug}/competitions/")


if __name__ == "__main__":
    test_event_competitions()
