from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending AbstractUser with ML competition-specific fields.
    """
    email = models.EmailField(unique=True)
    elo_rating = models.IntegerField(default=1500)
    highest_rating = models.IntegerField(default=1500)
    competitions_participated = models.IntegerField(default=0)
    kaggle_username = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-elo_rating']
        indexes = [
            models.Index(fields=['-elo_rating']),
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.username

    def update_rating(self, new_rating):
        """Update user rating and highest rating if applicable."""
        self.elo_rating = new_rating
        if new_rating > self.highest_rating:
            self.highest_rating = new_rating
        self.save(update_fields=['elo_rating', 'highest_rating', 'updated_at'])

    def increment_competitions(self):
        """Increment the competitions participated counter."""
        self.competitions_participated += 1
        self.save(update_fields=['competitions_participated', 'updated_at'])

    @property
    def rating_tier(self):
        """Return the rating tier name based on current ELO rating."""
        if self.elo_rating >= 2400:
            return 'Grandmaster'
        elif self.elo_rating >= 2200:
            return 'International Master'
        elif self.elo_rating >= 2000:
            return 'Master'
        elif self.elo_rating >= 1800:
            return 'Expert'
        elif self.elo_rating >= 1600:
            return 'Advanced'
        elif self.elo_rating >= 1400:
            return 'Intermediate'
        elif self.elo_rating >= 1200:
            return 'Beginner'
        else:
            return 'Newbie'
