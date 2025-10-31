from rest_framework import serializers
from .models import RatingHistory
from apps.users.serializers import UserLeaderboardSerializer
from apps.competitions.serializers import CompetitionListSerializer


class RatingHistorySerializer(serializers.ModelSerializer):
    """Serializer for RatingHistory model."""
    user = UserLeaderboardSerializer(read_only=True)
    competition = CompetitionListSerializer(read_only=True)
    is_positive = serializers.ReadOnlyField()

    class Meta:
        model = RatingHistory
        fields = [
            'id', 'user', 'competition', 'old_rating', 'new_rating',
            'rating_change', 'rank', 'timestamp', 'is_positive'
        ]
        read_only_fields = ['id', 'timestamp']


class RatingHistoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for rating history listing."""
    username = serializers.CharField(source='user.username', read_only=True)
    competition_title = serializers.CharField(source='competition.title', read_only=True)
    is_positive = serializers.ReadOnlyField()

    class Meta:
        model = RatingHistory
        fields = [
            'id', 'username', 'competition_title', 'old_rating',
            'new_rating', 'rating_change', 'rank', 'timestamp', 'is_positive'
        ]
