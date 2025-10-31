from django.db import models
from django.utils import timezone


class Competition(models.Model):
    """
    Model representing an ML competition.
    """
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    kaggle_competition_id = models.CharField(max_length=255, unique=True)
    kaggle_url = models.URLField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    rating_weight = models.FloatField(default=1.0)
    max_submissions_per_day = models.IntegerField(default=5)
    evaluation_metric = models.CharField(max_length=100, blank=True)
    prize_pool = models.CharField(max_length=255, blank=True)
    participants_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'competitions'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status', '-start_date']),
            models.Index(fields=['kaggle_competition_id']),
        ]

    def __str__(self):
        return self.title

    def update_status(self):
        """Update competition status based on current time."""
        now = timezone.now()
        if now < self.start_date:
            self.status = 'upcoming'
        elif self.start_date <= now <= self.end_date:
            self.status = 'ongoing'
        else:
            self.status = 'completed'
        self.save(update_fields=['status', 'updated_at'])

    @property
    def is_active(self):
        """Check if competition is currently ongoing."""
        return self.status == 'ongoing'

    @property
    def is_upcoming(self):
        """Check if competition hasn't started yet."""
        return self.status == 'upcoming'

    @property
    def is_completed(self):
        """Check if competition has ended."""
        return self.status == 'completed'

    @property
    def duration_days(self):
        """Calculate competition duration in days."""
        return (self.end_date - self.start_date).days

    def increment_participants(self):
        """Increment participants count."""
        self.participants_count += 1
        self.save(update_fields=['participants_count', 'updated_at'])
