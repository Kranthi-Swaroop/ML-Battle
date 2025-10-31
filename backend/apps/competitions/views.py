from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django.utils import timezone
from .models import Competition
from .serializers import (
    CompetitionSerializer,
    CompetitionListSerializer,
    CompetitionDetailSerializer
)


class CompetitionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Competition CRUD operations.
    """
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'kaggle_competition_id']
    ordering_fields = ['start_date', 'end_date', 'participants_count']
    ordering = ['-start_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return CompetitionListSerializer
        elif self.action == 'retrieve':
            return CompetitionDetailSerializer
        return CompetitionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def ongoing(self, request):
        """Get all ongoing competitions."""
        competitions = self.queryset.filter(status='ongoing')
        serializer = self.get_serializer(competitions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get all upcoming competitions."""
        competitions = self.queryset.filter(status='upcoming')
        serializer = self.get_serializer(competitions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get all completed competitions."""
        competitions = self.queryset.filter(status='completed')
        serializer = self.get_serializer(competitions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Get leaderboard for a specific competition."""
        competition = self.get_object()
        from apps.leaderboard.models import LeaderboardEntry
        from apps.leaderboard.serializers import LeaderboardEntrySerializer
        
        entries = LeaderboardEntry.objects.filter(
            competition=competition
        ).select_related('user').order_by('rank')
        
        serializer = LeaderboardEntrySerializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """Register current user for a competition."""
        competition = self.get_object()
        user = request.user

        if not competition.is_upcoming and not competition.is_active:
            return Response(
                {'error': 'Cannot register for completed competitions'},
                status=400
            )

        # Check if already registered
        from apps.leaderboard.models import LeaderboardEntry
        if LeaderboardEntry.objects.filter(user=user, competition=competition).exists():
            return Response(
                {'error': 'Already registered for this competition'},
                status=400
            )

        # Create leaderboard entry
        LeaderboardEntry.objects.create(
            user=user,
            competition=competition
        )
        
        competition.increment_participants()
        user.increment_competitions()

        return Response({'message': 'Successfully registered for competition'})
