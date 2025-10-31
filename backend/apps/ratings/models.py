from django.db import models
from django.conf import settings


class RatingHistory(models.Model):
    """
    Model representing a user's rating history after each competition.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rating_history')
    competition = models.ForeignKey('competitions.Competition', on_delete=models.CASCADE, related_name='rating_history')
    old_rating = models.IntegerField()
    new_rating = models.IntegerField()
    rating_change = models.IntegerField()
    rank = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rating_history'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['competition']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.competition.title} - {self.rating_change:+d}'

    @property
    def is_positive(self):
        """Check if rating change was positive."""
        return self.rating_change > 0
