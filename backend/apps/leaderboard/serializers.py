from rest_framework import serializers
from .models import LeaderboardEntry
from apps.users.serializers import UserLeaderboardSerializer


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    """Serializer for LeaderboardEntry model."""
    user = UserLeaderboardSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    elo_rating = serializers.IntegerField(source='user.elo_rating', read_only=True)
    rating_tier = serializers.CharField(source='user.rating_tier', read_only=True)

    class Meta:
        model = LeaderboardEntry
        fields = [
            'id', 'user', 'username', 'elo_rating', 'rating_tier',
            'best_score', 'rank', 'submissions_count', 'last_submission_time'
        ]
        read_only_fields = ['id']


class LeaderboardUpdateSerializer(serializers.Serializer):
    """Serializer for WebSocket leaderboard updates."""
    competition_id = serializers.IntegerField()
    entries = LeaderboardEntrySerializer(many=True)
    updated_at = serializers.DateTimeField()
