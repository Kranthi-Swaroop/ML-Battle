from celery import shared_task
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import RatingHistory
from .elo_calculator import EloRatingSystem
from apps.competitions.models import Competition
from apps.leaderboard.models import LeaderboardEntry
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def calculate_ratings_after_competition(competition_id: int):
    """
    Calculate and update ratings for all participants after competition ends.
    
    Args:
        competition_id: Database ID of the competition
    """
    try:
        competition = Competition.objects.get(id=competition_id)
        
        if competition.status != 'completed':
            logger.warning(f"Competition {competition.title} is not completed yet")
            return
        
        # Get all leaderboard entries for this competition
        entries = LeaderboardEntry.objects.filter(
            competition=competition
        ).select_related('user').order_by('rank')
        
        if not entries.exists():
            logger.warning(f"No participants found for {competition.title}")
            return
        
        # Prepare participant data
        participants = []
        for entry in entries:
            participants.append({
                'user_id': entry.user.id,
                'username': entry.user.username,
                'old_rating': entry.user.elo_rating,
                'rank': entry.rank,
            })
        
        # Calculate new ratings
        rating_results = EloRatingSystem.calculate_competition_ratings(
            participants,
            competition.rating_weight
        )
        
        # Update user ratings and create history records
        with transaction.atomic():
            for result in rating_results:
                user = User.objects.get(id=result['user_id'])
                
                # Create rating history record
                RatingHistory.objects.create(
                    user=user,
                    competition=competition,
                    old_rating=result['old_rating'],
                    new_rating=result['new_rating'],
                    rating_change=result['rating_change'],
                    rank=result['rank'],
                )
                
                # Update user's rating
                user.update_rating(result['new_rating'])
        
        logger.info(
            f"Successfully calculated ratings for {len(rating_results)} "
            f"participants in {competition.title}"
        )
        
        return f"Updated {len(rating_results)} user ratings"
        
    except Competition.DoesNotExist:
        logger.error(f"Competition {competition_id} not found")
    except Exception as e:
        logger.error(f"Error calculating ratings: {str(e)}")
        raise
