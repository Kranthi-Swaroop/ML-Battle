from rest_framework import serializers
from .models import LeaderboardEntry
from apps.users.serializers import UserLeaderboardSerializer


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    """Serializer for LeaderboardEntry model."""
    user = UserLeaderboardSerializer(read_only=True, allow_null=True)
    username = serializers.SerializerMethodField()
    elo_rating = serializers.SerializerMethodField()
    rating_tier = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = LeaderboardEntry
        fields = [
            'id', 'user', 'username', 'display_name', 'elo_rating', 'rating_tier',
            'best_score', 'score', 'rank', 'submissions_count', 'last_submission_time',
            'kaggle_team_name', 'submission_date'
        ]
        read_only_fields = ['id']
    
    def get_username(self, obj):
        """Get username or return None if user is None."""
        return obj.user.username if obj.user else None
    
    def get_elo_rating(self, obj):
        """Get elo rating or return None if user is None."""
        return obj.user.elo_rating if obj.user else None
    
    def get_rating_tier(self, obj):
        """Get rating tier or return None if user is None."""
        return obj.user.rating_tier if obj.user else None
    
    def get_display_name(self, obj):
        """Get display name - username for platform users, kaggle_team_name for Kaggle-only participants."""
        if obj.user:
            return obj.user.username
        return obj.kaggle_team_name or 'Unknown'


class LeaderboardUpdateSerializer(serializers.Serializer):
    """Serializer for WebSocket leaderboard updates."""
    competition_id = serializers.IntegerField()
    entries = LeaderboardEntrySerializer(many=True)
    updated_at = serializers.DateTimeField()
