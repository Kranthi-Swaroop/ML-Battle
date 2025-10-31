"""
Example: Creating competitions in events with automatic Kaggle sync
Demonstrates how competitions automatically sync when created/imported
"""
import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.utils import timezone
from apps.competitions.models import Competition, CompetitionEvent


def example_1_create_standalone_competition():
    """
    Example 1: Create standalone competition
    → Auto-sync triggers immediately
    """
    print("\n" + "="*100)
    print("EXAMPLE 1: Create Standalone Competition")
    print("="*100)
    
    competition = Competition.objects.create(
        title="Spaceship Titanic - Machine Learning",
        description="Predict which passengers are transported to an alternate dimension",
        kaggle_competition_id="spaceship-titanic",
        kaggle_url="https://www.kaggle.com/competitions/spaceship-titanic",
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=30),
        status='ongoing',
        rating_weight=1.0,
        max_submissions_per_day=5,
        evaluation_metric="Accuracy",
        prize_pool="$10,000"
    )
    
    print(f"✅ Created: {competition.title}")
    print(f"   Kaggle ID: {competition.kaggle_competition_id}")
    print(f"   Status: {competition.status}")
    print(f"   🚀 AUTO-SYNC TRIGGERED! (Check Celery worker logs)")
    print("="*100)
    
    return competition


def example_2_create_event_with_competitions():
    """
    Example 2: Create event with multiple competitions
    → Each competition auto-syncs independently
    """
    print("\n" + "="*100)
    print("EXAMPLE 2: Create Event with Multiple Competitions")
    print("="*100)
    
    # Create parent event
    event = CompetitionEvent.objects.create(
        title="Neural Night 2025",
        description="Premier ML competition event",
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=7),
        status='ongoing',
        organizer="ML-Battle Team",
        total_prize_pool="$50,000",
        is_featured=True
    )
    
    print(f"✅ Created Event: {event.title}")
    print(f"   Duration: {event.duration_days} days")
    print(f"\n   Adding competitions to event...\n")
    
    # Add multiple competitions to event
    competitions_data = [
        {
            'title': 'Titanic - Machine Learning from Disaster',
            'kaggle_id': 'titanic',
            'description': 'Classic ML competition',
            'metric': 'Accuracy'
        },
        {
            'title': 'House Prices - Advanced Regression',
            'kaggle_id': 'house-prices-advanced-regression-techniques',
            'description': 'Predict house prices',
            'metric': 'RMSE'
        },
        {
            'title': 'Digit Recognizer',
            'kaggle_id': 'digit-recognizer',
            'description': 'MNIST digit classification',
            'metric': 'Accuracy'
        }
    ]
    
    created_competitions = []
    
    for idx, comp_data in enumerate(competitions_data, 1):
        competition = Competition.objects.create(
            event=event,  # Link to parent event
            title=comp_data['title'],
            description=comp_data['description'],
            kaggle_competition_id=comp_data['kaggle_id'],
            kaggle_url=f"https://www.kaggle.com/c/{comp_data['kaggle_id']}",
            start_date=event.start_date,
            end_date=event.end_date,
            status='ongoing',
            rating_weight=1.0,
            evaluation_metric=comp_data['metric'],
            max_submissions_per_day=5
        )
        
        created_competitions.append(competition)
        
        print(f"   {idx}. ✅ {competition.title}")
        print(f"      Kaggle ID: {competition.kaggle_competition_id}")
        print(f"      🚀 AUTO-SYNC TRIGGERED!")
        print()
    
    print(f"✅ Event Setup Complete!")
    print(f"   Total Competitions: {len(created_competitions)}")
    print(f"   All {len(created_competitions)} competitions are syncing in background!")
    print("="*100)
    
    return event, created_competitions


def example_3_import_from_kaggle_list():
    """
    Example 3: Bulk import from Kaggle competition list
    → Each triggers auto-sync
    """
    print("\n" + "="*100)
    print("EXAMPLE 3: Bulk Import from Kaggle List")
    print("="*100)
    
    # Simulate importing competitions from Kaggle API or CSV
    kaggle_competitions = [
        {'title': 'NLP with Disaster Tweets', 'slug': 'nlp-getting-started'},
        {'title': 'Store Sales - Time Series', 'slug': 'store-sales-time-series-forecasting'},
        {'title': 'Playground Series S4E1', 'slug': 'playground-series-s4e1'},
    ]
    
    imported = []
    
    print(f"Importing {len(kaggle_competitions)} competitions...\n")
    
    for idx, kaggle_comp in enumerate(kaggle_competitions, 1):
        competition = Competition.objects.create(
            title=kaggle_comp['title'],
            description=f"Imported from Kaggle: {kaggle_comp['slug']}",
            kaggle_competition_id=kaggle_comp['slug'],
            kaggle_url=f"https://www.kaggle.com/c/{kaggle_comp['slug']}",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=60),
            status='ongoing',
            rating_weight=1.0,
            max_submissions_per_day=5
        )
        
        imported.append(competition)
        
        print(f"   {idx}. ✅ Imported: {competition.title}")
        print(f"      🚀 AUTO-SYNC TRIGGERED!")
    
    print(f"\n✅ Bulk Import Complete!")
    print(f"   {len(imported)} competitions syncing...")
    print("="*100)
    
    return imported


def example_4_activate_upcoming_competition():
    """
    Example 4: Activate upcoming competition
    → Status change triggers sync
    """
    print("\n" + "="*100)
    print("EXAMPLE 4: Activate Upcoming Competition")
    print("="*100)
    
    # Create as upcoming
    competition = Competition.objects.create(
        title="Future Competition",
        description="Starts next week",
        kaggle_competition_id="future-comp",
        start_date=timezone.now() + timedelta(days=7),
        end_date=timezone.now() + timedelta(days=37),
        status='upcoming',  # Not synced yet
        rating_weight=1.0,
        max_submissions_per_day=5
    )
    
    print(f"✅ Created upcoming competition: {competition.title}")
    print(f"   Status: {competition.status}")
    print(f"   ℹ️  Auto-sync NOT triggered (status is 'upcoming')\n")
    
    # Later: activate it
    print("   Activating competition now...\n")
    competition.status = 'ongoing'
    competition.save()
    
    print(f"✅ Status changed to: {competition.status}")
    print(f"   🚀 AUTO-SYNC TRIGGERED! (Status change to 'ongoing')")
    print("="*100)
    
    return competition


def verify_sync_results(competition):
    """
    Verify that sync happened by checking LeaderboardEntry
    """
    from apps.leaderboard.models import LeaderboardEntry
    import time
    
    print("\n" + "="*100)
    print("VERIFYING SYNC RESULTS")
    print("="*100)
    
    print(f"Competition: {competition.title}")
    print(f"Kaggle ID: {competition.kaggle_competition_id}")
    print("\nWaiting for sync to complete (20 seconds)...")
    
    # Wait for background task
    for i in range(4):
        time.sleep(5)
        entries = LeaderboardEntry.objects.filter(competition=competition)
        print(f"   [{(i+1)*5}s] Checking... Found {entries.count()} entries")
    
    final_count = LeaderboardEntry.objects.filter(competition=competition).count()
    
    print(f"\n{'='*100}")
    if final_count > 0:
        print(f"✅ SUCCESS! Sync completed: {final_count} leaderboard entries")
        
        # Show top 5
        top_entries = LeaderboardEntry.objects.filter(
            competition=competition
        ).order_by('rank')[:5]
        
        print(f"\nTop 5 Entries:")
        for entry in top_entries:
            print(f"   {entry.rank}. {entry.user.username} - Score: {entry.score}")
    else:
        print("⏳ Sync still in progress or no matching users found")
        print("   (This is normal if your database doesn't have users matching Kaggle usernames)")
    
    print("="*100)


def main():
    """Run all examples"""
    print("\n" + "#"*100)
    print("# AUTOMATIC KAGGLE SYNC EXAMPLES")
    print("#"*100)
    
    print("\nThese examples show how competitions automatically sync when created.")
    print("Watch your Celery worker logs to see sync tasks executing!\n")
    
    # Run examples
    try:
        # Example 1: Simple standalone
        comp1 = example_1_create_standalone_competition()
        
        # Example 2: Event with competitions
        event, competitions = example_2_create_event_with_competitions()
        
        # Example 3: Bulk import
        imported = example_3_import_from_kaggle_list()
        
        # Example 4: Activate upcoming
        comp4 = example_4_activate_upcoming_competition()
        
        print("\n" + "#"*100)
        print("# ALL EXAMPLES COMPLETE!")
        print("#"*100)
        print("\n✅ All competitions created and auto-sync triggered!")
        print("\n📋 Summary:")
        print(f"   - Standalone competitions: 1")
        print(f"   - Event competitions: {len(competitions)}")
        print(f"   - Bulk imported: {len(imported)}")
        print(f"   - Activated: 1")
        print(f"   - TOTAL: {1 + len(competitions) + len(imported) + 1} competitions")
        print("\n🔍 Check Celery worker logs to see sync tasks executing!")
        print("   Look for: '🚀 Auto-triggering Kaggle sync'")
        
        # Optional: Verify one
        print("\n" + "="*100)
        response = input("\nWant to verify sync for 'Spaceship Titanic'? (y/n): ")
        if response.lower() == 'y':
            verify_sync_results(comp1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("   1. Django is configured properly")
        print("   2. Database is migrated")
        print("   3. Celery worker is running")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
