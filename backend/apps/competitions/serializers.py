from rest_framework import serializers
from .models import Competition


class CompetitionSerializer(serializers.ModelSerializer):
    """Serializer for Competition model."""
    is_active = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Competition
        fields = [
            'id', 'title', 'description', 'kaggle_competition_id', 'kaggle_url',
            'start_date', 'end_date', 'status', 'rating_weight',
            'max_submissions_per_day', 'evaluation_metric', 'prize_pool',
            'participants_count', 'is_active', 'is_upcoming', 'is_completed',
            'duration_days', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'participants_count', 'created_at', 'updated_at']


class CompetitionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for competition listing."""
    is_active = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Competition
        fields = [
            'id', 'title', 'kaggle_competition_id', 'start_date', 'end_date',
            'status', 'participants_count', 'is_active', 'duration_days',
            'evaluation_metric', 'prize_pool'
        ]


class CompetitionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single competition view."""
    is_active = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Competition
        fields = '__all__'
