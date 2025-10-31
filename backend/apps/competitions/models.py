from django.db import models
from django.utils import timezone


class CompetitionEvent(models.Model):
    """
    Model representing a competition event (parent competition).
    Example: "Neural Night", "AI Challenge 2025", etc.
    """
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(max_length=255, unique=True)
    banner_image = models.URLField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    organizer = models.CharField(max_length=255, blank=True)
    total_prize_pool = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)
    participants_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'competition_events'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status', '-start_date']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-generate unique slug from title."""
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            
            # Ensure unique slug
            while CompetitionEvent.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == 'ongoing'

    @property
    def competition_count(self):
        """Get count of sub-competitions."""
        return self.competitions.count()

    def update_status(self):
        """Update event status based on current time."""
        now = timezone.now()
        if now < self.start_date:
            self.status = 'upcoming'
        elif self.start_date <= now <= self.end_date:
            self.status = 'ongoing'
        else:
            self.status = 'completed'
        self.save(update_fields=['status', 'updated_at'])


class Competition(models.Model):
    """
    Model representing an ML competition.
    """
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    # Parent event relationship
    event = models.ForeignKey(
        CompetitionEvent,
        on_delete=models.CASCADE,
        related_name='competitions',
        null=True,
        blank=True,
        help_text='Parent competition event this competition belongs to'
    )
    
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
    
    # Scoring configuration for leaderboard calculation
    higher_is_better = models.BooleanField(
        default=True,
        help_text='True if higher metric value means better performance, False if lower is better'
    )
    metric_min_value = models.FloatField(
        default=0.0,
        help_text='Minimum value of the metric for normalization'
    )
    metric_max_value = models.FloatField(
        default=1.0,
        help_text='Maximum value of the metric for normalization'
    )
    points_for_perfect_score = models.FloatField(
        default=100.0,
        help_text='Maximum points awarded for perfect score (PS points)'
    )
    
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
