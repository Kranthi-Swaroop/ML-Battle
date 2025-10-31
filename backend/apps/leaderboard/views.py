from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import LeaderboardEntry
from .serializers import LeaderboardEntrySerializer


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing leaderboard entries.
    """
    queryset = LeaderboardEntry.objects.all().select_related('user', 'competition')
    serializer_class = LeaderboardEntrySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by competition if specified
        competition_id = self.request.query_params.get('competition', None)
        if competition_id:
            queryset = queryset.filter(competition_id=competition_id)
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('rank')
