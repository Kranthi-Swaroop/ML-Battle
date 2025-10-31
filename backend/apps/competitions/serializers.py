from rest_framework import serializers
from .models import Competition, CompetitionEvent


class CompetitionEventSerializer(serializers.ModelSerializer):
    """Serializer for CompetitionEvent model."""
    is_active = serializers.ReadOnlyField()
    competition_count = serializers.ReadOnlyField()

    class Meta:
        model = CompetitionEvent
        fields = [
            'id', 'title', 'description', 'slug', 'banner_image',
            'start_date', 'end_date', 'status', 'organizer',
            'total_prize_pool', 'is_featured', 'participants_count',
            'is_active', 'competition_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'status', 'participants_count', 'created_at', 'updated_at']


class CompetitionEventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for event listing."""
    competition_count = serializers.ReadOnlyField()

    class Meta:
        model = CompetitionEvent
        fields = [
            'id', 'title', 'slug', 'banner_image', 'start_date', 'end_date',
            'status', 'total_prize_pool', 'is_featured', 'competition_count'
        ]


class CompetitionEventDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested competitions."""
    competitions = serializers.SerializerMethodField()
    competition_count = serializers.ReadOnlyField()

    class Meta:
        model = CompetitionEvent
        fields = '__all__'

    def get_competitions(self, obj):
        # Use prefetched data if available, otherwise query
        competitions = obj.competitions.all()
        return CompetitionListSerializer(competitions, many=True).data


class CompetitionSerializer(serializers.ModelSerializer):
    """Serializer for Competition model."""
    is_active = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()
    event_title = serializers.SerializerMethodField()

    class Meta:
        model = Competition
        fields = [
            'id', 'event', 'event_title', 'title', 'description', 'kaggle_competition_id', 'kaggle_url',
            'start_date', 'end_date', 'status', 'rating_weight',
            'max_submissions_per_day', 'evaluation_metric', 'prize_pool',
            'participants_count', 'is_active', 'is_upcoming', 'is_completed',
            'duration_days', 'higher_is_better', 'metric_min_value', 
            'metric_max_value', 'points_for_perfect_score', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'participants_count', 'created_at', 'updated_at']
    
    def get_event_title(self, obj):
        """Safely get event title."""
        return obj.event.title if obj.event else None


class CompetitionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for competition listing."""
    is_active = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()
    event_title = serializers.SerializerMethodField()

    class Meta:
        model = Competition
        fields = [
            'id', 'event', 'event_title', 'title', 'kaggle_competition_id', 'start_date', 'end_date',
            'status', 'participants_count', 'is_active', 'duration_days',
            'evaluation_metric', 'prize_pool'
        ]
    
    def get_event_title(self, obj):
        """Safely get event title."""
        return obj.event.title if obj.event else None


class CompetitionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single competition view."""
    is_active = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Competition
        fields = '__all__'
