from celery import shared_task
from django.utils import timezone
from .models import Competition
import logging

logger = logging.getLogger(__name__)


@shared_task
def sync_competition_leaderboard_task(competition_id):
    """
    Sync leaderboard for a single competition (triggered by signal).
    This is called automatically when a competition is created or updated.
    
    Args:
        competition_id: ID of the Competition to sync
    
    Returns:
        dict: Sync results with success status and entry count
    """
    from .kaggle_leaderboard_sync import KaggleLeaderboardSync
    
    try:
        competition = Competition.objects.get(id=competition_id)
        
        if not competition.kaggle_competition_id:
            return {
                'success': False,
                'error': 'No kaggle_competition_id set',
                'competition': competition.title
            }
        
        syncer = KaggleLeaderboardSync()
        result = syncer.sync_competition_leaderboard(competition)
        
        logger.info(
            f"✅ Auto-sync complete for '{competition.title}': "
            f"{result['entries_processed']} entries processed"
        )
        
        return result
        
    except Competition.DoesNotExist:
        error_msg = f"Competition with ID {competition_id} not found"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    except Exception as e:
        error_msg = f"Error syncing competition {competition_id}: {e}"
        logger.error(error_msg)
        return {'success': False, 'error': str(e)}


@shared_task
def update_competition_statuses():
    """
    Update status of all competitions based on current time.
    """
    competitions = Competition.objects.all()
    updated_count = 0
    
    for competition in competitions:
        old_status = competition.status
        competition.update_status()
        
        if old_status != competition.status:
            updated_count += 1
            
            # If competition just ended, trigger rating calculation
            if competition.status == 'completed' and old_status == 'ongoing':
                from apps.ratings.tasks import calculate_ratings_after_competition
                calculate_ratings_after_competition.delay(competition.id)
    
    return f'Updated {updated_count} competition statuses'


@shared_task
def sync_kaggle_leaderboard_auto():
    """
    Automatically sync leaderboard from Kaggle for all active competitions.
    Process: Fetch -> Save CSV -> Update DB -> Delete CSV
    Runs every 5 minutes.
    """
    import logging
    from .kaggle_leaderboard_sync import KaggleLeaderboardSync
    
    logger = logging.getLogger(__name__)
    
    # Get all active competitions with Kaggle ID
    active_competitions = Competition.objects.filter(
        status='ongoing',
        kaggle_competition_id__isnull=False
    ).exclude(kaggle_competition_id='')
    
    if not active_competitions.exists():
        return 'No active Kaggle competitions to sync'
    
    syncer = KaggleLeaderboardSync()
    results = []
    
    for competition in active_competitions:
        try:
            result = syncer.sync_competition_leaderboard(competition)
            results.append(result)
            logger.info(f"Synced {competition.title}: {result['entries_processed']} entries")
        except Exception as e:
            logger.error(f"Error syncing {competition.title}: {e}")
            results.append({
                'success': False,
                'competition': competition.title,
                'error': str(e)
            })
    
    # Cleanup old CSV files
    syncer.cleanup_old_files()
    
    total_synced = sum(r['entries_processed'] for r in results if r['success'])
    return f'Synced {total_synced} entries across {len(results)} competitions'


@shared_task
def sync_kaggle_submissions():
    """
    Legacy task - kept for backward compatibility.
    Use sync_kaggle_leaderboard_auto instead.
    """
    import logging
    from apps.submissions.kaggle_service import get_kaggle_service
    from apps.submissions.models import Submission
    from apps.leaderboard.models import LeaderboardEntry
    from apps.users.models import User
    from dateutil import parser
    from django.utils import timezone
    
    logger = logging.getLogger(__name__)
    
    # Get all active competitions with Kaggle ID
    active_competitions = Competition.objects.filter(
        status='ongoing',
        kaggle_competition_id__isnull=False
    ).exclude(kaggle_competition_id='')
    
    if not active_competitions.exists():
        return 'No active Kaggle competitions to sync'
    
    kaggle_service = get_kaggle_service()
    total_synced = 0
    
    for competition in active_competitions:
        try:
            logger.info(f"Syncing {competition.title} (ID: {competition.id})")
            
            # Fetch submissions from Kaggle
            submissions_data = kaggle_service.get_all_competition_submissions(
                competition.kaggle_competition_id
            )
            
            if not submissions_data:
                logger.warning(f"No data fetched for {competition.title}")
                continue
            
            # Get registered users for this competition
            registered_users = LeaderboardEntry.objects.filter(
                competition=competition,
                user__isnull=False
            ).values_list('user__username', flat=True)
            
            submissions_created = 0
            leaderboard_updated = 0
            rank_counter = 1
            
            for sub_data in submissions_data:
                team_name = sub_data['team_name']
                score = sub_data['score']
                submission_date = sub_data.get('submission_date')
                
                # Find matching user
                user = User.objects.filter(username=team_name).first()
                
                # Only process registered users
                if not user or team_name not in registered_users:
                    continue
                
                # Parse date
                parsed_date = None
                if submission_date:
                    try:
                        parsed_date = parser.parse(submission_date)
                    except:
                        parsed_date = timezone.now()
                else:
                    parsed_date = timezone.now()
                
                # Create submission if not exists
                submission, created = Submission.objects.get_or_create(
                    user=user,
                    competition=competition,
                    score=score,
                    defaults={
                        'public_score': score,
                        'submission_time': parsed_date,
                        'status': 'completed',
                        'kaggle_submission_id': f"{team_name}_{score}"
                    }
                )
                
                if created:
                    submissions_created += 1
                
                # Update leaderboard
                leaderboard_entry = LeaderboardEntry.objects.get(
                    competition=competition,
                    user=user
                )
                
                leaderboard_entry.rank = rank_counter
                leaderboard_entry.kaggle_team_name = team_name
                leaderboard_entry.score = score
                leaderboard_entry.submission_date = parsed_date
                leaderboard_entry.last_submission_time = parsed_date
                leaderboard_entry.submissions_count = leaderboard_entry.submissions_count + 1
                
                if score and (not leaderboard_entry.best_score or score > leaderboard_entry.best_score):
                    leaderboard_entry.best_score = score
                
                leaderboard_entry.save()
                leaderboard_updated += 1
                rank_counter += 1
            
            logger.info(f"Synced {competition.title}: {submissions_created} submissions, {leaderboard_updated} leaderboard entries")
            total_synced += 1
            
        except Exception as e:
            logger.error(f"Error syncing {competition.title}: {str(e)}")
            continue
    
    return f'Synced {total_synced} competitions'
