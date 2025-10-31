from django.db import models
from django.conf import settings


class Submission(models.Model):
    """
    Model representing a user's submission to a competition.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    competition = models.ForeignKey('competitions.Competition', on_delete=models.CASCADE, related_name='submissions')
    kaggle_submission_id = models.CharField(max_length=255, blank=True)
    score = models.FloatField(null=True, blank=True)
    public_score = models.FloatField(null=True, blank=True)
    private_score = models.FloatField(null=True, blank=True)
    submission_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='submitted')
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'submissions'
        ordering = ['-submission_time']
        indexes = [
            models.Index(fields=['user', 'competition']),
            models.Index(fields=['competition', '-score']),
            models.Index(fields=['-submission_time']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.competition.title} - {self.score}'

    @property
    def is_best_submission(self):
        """Check if this is the user's best submission for this competition."""
        from apps.leaderboard.models import LeaderboardEntry
        try:
            entry = LeaderboardEntry.objects.get(user=self.user, competition=self.competition)
            return self.score == entry.best_score
        except LeaderboardEntry.DoesNotExist:
            return False
