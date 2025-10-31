from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    UserProfileSerializer, UserLeaderboardSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserProfileSerializer
        elif self.action == 'list':
            return UserLeaderboardSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile."""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def rating_history(self, request, pk=None):
        """Get rating history for a specific user."""
        user = self.get_object()
        from apps.ratings.models import RatingHistory
        from apps.ratings.serializers import RatingHistorySerializer
        
        history = RatingHistory.objects.filter(user=user).select_related('competition')
        serializer = RatingHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Get all submissions for a specific user."""
        user = self.get_object()
        from apps.submissions.models import Submission
        from apps.submissions.serializers import SubmissionSerializer
        
        submissions = Submission.objects.filter(user=user).select_related('competition')
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
