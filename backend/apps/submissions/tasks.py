from celery import shared_task
from django.db import transaction
from django.contrib.auth import get_user_model
from .kaggle_service import get_kaggle_service
from .models import Submission
from apps.competitions.models import Competition
from apps.leaderboard.models import LeaderboardEntry
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def fetch_kaggle_leaderboard(competition_id: int):
    """
    Fetch and update leaderboard data from Kaggle for a specific competition.
    
    Args:
        competition_id: Database ID of the competition
    """
    try:
        competition = Competition.objects.get(id=competition_id)
        
        if not competition.is_active:
            logger.info(f"Skipping inactive competition: {competition.title}")
            return
        
        # Get Kaggle service and fetch leaderboard
        kaggle_service = get_kaggle_service()
        leaderboard_data = kaggle_service.get_competition_leaderboard(
            competition.kaggle_competition_id
        )
        
        if not leaderboard_data:
            logger.warning(f"No leaderboard data for {competition.title}")
            return
        
        # Update leaderboard entries
        updated_count = 0
        with transaction.atomic():
            for entry_data in leaderboard_data:
                # Try to match Kaggle team name with platform username
                # First try exact match, then try Kaggle username field
                user = None
                try:
                    user = User.objects.get(username=entry_data['team_name'])
                except User.DoesNotExist:
                    try:
                        user = User.objects.get(kaggle_username=entry_data['team_name'])
                    except User.DoesNotExist:
                        logger.debug(f"No user found for Kaggle team: {entry_data['team_name']}")
                        continue
                
                # Update or create leaderboard entry
                entry, created = LeaderboardEntry.objects.update_or_create(
                    user=user,
                    competition=competition,
                    defaults={
                        'best_score': entry_data['score'],
                        'rank': entry_data['rank'],
                    }
                )
                
                if created:
                    entry.submissions_count = 1
                else:
                    entry.submissions_count += 1
                entry.save()
                
                # Create submission record
                Submission.objects.create(
                    user=user,
                    competition=competition,
                    score=entry_data['score'],
                    status='complete'
                )
                
                updated_count += 1
        
        logger.info(f"Updated {updated_count} leaderboard entries for {competition.title}")
        
        # Send WebSocket update
        from apps.leaderboard.consumers import send_leaderboard_update
        send_leaderboard_update(competition.id)
        
        return f"Updated {updated_count} entries"
        
    except Competition.DoesNotExist:
        logger.error(f"Competition {competition_id} not found")
    except Exception as e:
        logger.error(f"Error fetching Kaggle leaderboard: {str(e)}")
        raise


@shared_task
def fetch_all_active_competitions():
    """
    Fetch leaderboard data for all active competitions.
    """
    active_competitions = Competition.objects.filter(status='ongoing')
    
    for competition in active_competitions:
        fetch_kaggle_leaderboard.delay(competition.id)
    
    return f"Triggered updates for {active_competitions.count()} active competitions"
