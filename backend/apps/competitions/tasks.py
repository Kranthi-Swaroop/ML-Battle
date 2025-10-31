from celery import shared_task
from django.utils import timezone
from .models import Competition


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
