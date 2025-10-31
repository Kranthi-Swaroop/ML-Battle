from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import RatingHistory
from .serializers import RatingHistorySerializer, RatingHistoryListSerializer


class RatingHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing rating history.
    """
    queryset = RatingHistory.objects.all().select_related('user', 'competition')
    serializer_class = RatingHistorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return RatingHistoryListSerializer
        return RatingHistorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by competition if specified
        competition_id = self.request.query_params.get('competition', None)
        if competition_id:
            queryset = queryset.filter(competition_id=competition_id)
        
        return queryset
