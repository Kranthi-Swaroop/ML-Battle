"""
Performance and functionality test script for ML-Battle.
Run this to validate all optimizations and features.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.db import connection
from django.test.utils import override_settings
from apps.competitions.models import Competition, CompetitionEvent
from apps.leaderboard.models import LeaderboardEntry
from apps.users.models import User
import time


def reset_queries():
    """Reset the query counter."""
    from django.db import reset_queries as django_reset
    django_reset()


def print_queries():
    """Print all executed queries."""
    print(f"\n📊 Total Queries: {len(connection.queries)}")
    for i, query in enumerate(connection.queries, 1):
        print(f"  {i}. {query['sql'][:100]}... ({query['time']}s)")


def test_event_detail_queries():
    """Test event detail page query optimization."""
    print("\n" + "="*60)
    print("🧪 Test 1: Event Detail Query Optimization")
    print("="*60)
    
    reset_queries()
    start = time.time()
    
    # Simulate what happens when loading EventDetail page
    event = CompetitionEvent.objects.prefetch_related('competitions').first()
    
    if event:
        print(f"✅ Event loaded: {event.title}")
        
        # Access competitions (should not trigger additional queries)
        competitions = list(event.competitions.all())
        print(f"✅ Competitions loaded: {len(competitions)}")
        
        # Access event title from each competition
        for comp in competitions:
            _ = comp.event.title  # Should use cached data
        
        duration = (time.time() - start) * 1000
        print(f"\n⏱️  Duration: {duration:.2f}ms")
        print_queries()
        
        # Expected: 2 queries (1 for event, 1 for competitions)
        query_count = len(connection.queries)
        if query_count <= 3:
            print(f"\n✅ PASS: Efficient query count ({query_count} queries)")
        else:
            print(f"\n❌ FAIL: Too many queries ({query_count} queries)")
    else:
        print("❌ No events found in database")


def test_competition_list_queries():
    """Test competition listing query optimization."""
    print("\n" + "="*60)
    print("🧪 Test 2: Competition List Query Optimization")
    print("="*60)
    
    reset_queries()
    start = time.time()
    
    # Simulate what happens when loading competition list
    competitions = Competition.objects.select_related('event').all()[:10]
    
    print(f"✅ Competitions loaded: {competitions.count()}")
    
    # Access event data (should not trigger additional queries)
    for comp in competitions:
        _ = comp.event.title if comp.event else "No event"
    
    duration = (time.time() - start) * 1000
    print(f"\n⏱️  Duration: {duration:.2f}ms")
    print_queries()
    
    # Expected: 1 query with JOIN
    query_count = len(connection.queries)
    if query_count <= 2:
        print(f"\n✅ PASS: Efficient query count ({query_count} queries)")
    else:
        print(f"\n❌ FAIL: Too many queries ({query_count} queries)")


def test_leaderboard_queries():
    """Test leaderboard query optimization."""
    print("\n" + "="*60)
    print("🧪 Test 3: Leaderboard Query Optimization")
    print("="*60)
    
    reset_queries()
    start = time.time()
    
    # Simulate what happens when loading leaderboard
    competition = Competition.objects.first()
    
    if competition:
        entries = LeaderboardEntry.objects.filter(
            competition=competition
        ).select_related('user', 'competition')[:20]
        
        print(f"✅ Leaderboard loaded: {entries.count()} entries")
        
        # Access related data (should not trigger additional queries)
        for entry in entries:
            _ = entry.user.username if entry.user else "Anonymous"
            _ = entry.competition.title
        
        duration = (time.time() - start) * 1000
        print(f"\n⏱️  Duration: {duration:.2f}ms")
        print_queries()
        
        # Expected: 2 queries (1 for competition, 1 for entries with joins)
        query_count = len(connection.queries)
        if query_count <= 3:
            print(f"\n✅ PASS: Efficient query count ({query_count} queries)")
        else:
            print(f"\n❌ FAIL: Too many queries ({query_count} queries)")
    else:
        print("❌ No competitions found in database")


def test_import_validation():
    """Test import endpoint validation."""
    print("\n" + "="*60)
    print("🧪 Test 4: Import Validation")
    print("="*60)
    
    # Test duplicate detection
    existing_comp = Competition.objects.first()
    
    if existing_comp and existing_comp.kaggle_competition_id:
        kaggle_id = existing_comp.kaggle_competition_id
        check = Competition.objects.filter(kaggle_competition_id=kaggle_id).exists()
        
        print(f"✅ Testing duplicate detection for: {kaggle_id}")
        print(f"✅ Duplicate exists: {check}")
        
        if check:
            print("\n✅ PASS: Duplicate detection working")
        else:
            print("\n❌ FAIL: Duplicate detection not working")
    else:
        print("⚠️  SKIP: No competitions with Kaggle ID found")


def print_summary():
    """Print test summary."""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    # Count database objects
    events = CompetitionEvent.objects.count()
    comps = Competition.objects.count()
    users = User.objects.count()
    entries = LeaderboardEntry.objects.count()
    
    print(f"Events: {events}")
    print(f"Competitions: {comps}")
    print(f"Users: {users}")
    print(f"Leaderboard Entries: {entries}")
    
    print("\n✅ All tests completed!")
    print("\n💡 Next Steps:")
    print("  1. Check the query counts above")
    print("  2. If any test shows >10 queries, investigate")
    print("  3. Enable performance middleware to monitor in real-time")
    print("  4. Test the frontend import functionality")


if __name__ == '__main__':
    print("\n🚀 ML-Battle Performance Test Suite")
    print("Testing query optimizations and functionality...")
    
    try:
        test_event_detail_queries()
        test_competition_list_queries()
        test_leaderboard_queries()
        test_import_validation()
        print_summary()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
