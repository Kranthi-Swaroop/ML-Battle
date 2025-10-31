from rest_framework import serializers
from .models import Submission
from apps.users.serializers import UserLeaderboardSerializer
from apps.competitions.serializers import CompetitionListSerializer


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model."""
    user = UserLeaderboardSerializer(read_only=True)
    competition = CompetitionListSerializer(read_only=True)
    is_best_submission = serializers.ReadOnlyField()

    class Meta:
        model = Submission
        fields = [
            'id', 'user', 'competition', 'kaggle_submission_id',
            'score', 'public_score', 'private_score', 'submission_time',
            'status', 'error_message', 'is_best_submission'
        ]
        read_only_fields = ['id', 'submission_time']


class SubmissionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for submission listing."""
    username = serializers.CharField(source='user.username', read_only=True)
    competition_title = serializers.CharField(source='competition.title', read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id', 'username', 'competition_title', 'score',
            'submission_time', 'status'
        ]
