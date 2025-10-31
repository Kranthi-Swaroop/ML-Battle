from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Submission
from .serializers import SubmissionSerializer, SubmissionListSerializer


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing submissions.
    Read-only as submissions come from Kaggle.
    """
    queryset = Submission.objects.all().select_related('user', 'competition')
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return SubmissionListSerializer
        return SubmissionSerializer

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
