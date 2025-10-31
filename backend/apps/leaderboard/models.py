from django.db import models
from django.conf import settings


class LeaderboardEntry(models.Model):
    """
    Model representing a user's standing in a competition leaderboard.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leaderboard_entries')
    competition = models.ForeignKey('competitions.Competition', on_delete=models.CASCADE, related_name='leaderboard_entries')
    best_score = models.FloatField(default=0.0)
    rank = models.IntegerField(default=0)
    submissions_count = models.IntegerField(default=0)
    last_submission_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'leaderboard_entries'
        unique_together = ['user', 'competition']
        ordering = ['rank']
        indexes = [
            models.Index(fields=['competition', 'rank']),
            models.Index(fields=['user', 'competition']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.competition.title} - Rank {self.rank}'

    def update_best_score(self, new_score):
        """Update best score if the new score is better."""
        # Assuming higher score is better - adjust based on competition metric
        if new_score > self.best_score:
            self.best_score = new_score
            self.save(update_fields=['best_score'])
            return True
        return False
