"""
Django signals for automatic Kaggle leaderboard sync
Automatically triggers sync when:
1. A new competition is created with kaggle_competition_id
2. An existing competition's kaggle_competition_id is updated
3. A competition's status changes to 'ongoing'
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Competition
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Competition)
def auto_sync_kaggle_leaderboard(sender, instance, created, **kwargs):
    """
    Automatically sync Kaggle leaderboard when:
    - New competition is created with kaggle_competition_id
    - Existing competition gets kaggle_competition_id added
    - Competition becomes active (status='ongoing')
    """
    # Only sync if competition has kaggle_competition_id
    if not instance.kaggle_competition_id:
        return
    
    # Determine if we should sync
    should_sync = False
    reason = ""
    
    if created:
        # New competition created
        should_sync = True
        reason = "New competition created"
    elif instance.status == 'ongoing':
        # Competition is active
        should_sync = True
        reason = "Competition is active"
    
    if should_sync:
        logger.info(f"🚀 Auto-triggering Kaggle sync for '{instance.title}' ({reason})")
        
        # Import here to avoid circular imports
        from .tasks import sync_competition_leaderboard_task
        
        # Trigger async sync via Celery
        sync_competition_leaderboard_task.delay(instance.id)
        
        logger.info(f"✅ Sync task queued for competition: {instance.title}")


@receiver(post_save, sender=Competition)
def log_competition_changes(sender, instance, created, **kwargs):
    """
    Log competition creation and updates for monitoring
    """
    if created:
        logger.info(
            f"📝 New Competition Created:\n"
            f"   Title: {instance.title}\n"
            f"   Kaggle ID: {instance.kaggle_competition_id}\n"
            f"   Status: {instance.status}\n"
            f"   Event: {instance.event.title if instance.event else 'Standalone'}"
        )
    else:
        logger.debug(f"📝 Competition Updated: {instance.title}")
