from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django.utils import timezone
from .models import Competition, CompetitionEvent
from .serializers import (
    CompetitionSerializer,
    CompetitionListSerializer,
    CompetitionDetailSerializer,
    CompetitionEventSerializer,
    CompetitionEventListSerializer,
    CompetitionEventDetailSerializer
)


class CompetitionEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CompetitionEvent CRUD operations.
    """
    queryset = CompetitionEvent.objects.all().prefetch_related('competitions')
    serializer_class = CompetitionEventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'organizer']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return CompetitionEventListSerializer
        elif self.action == 'retrieve':
            return CompetitionEventDetailSerializer
        return CompetitionEventSerializer

    def get_permissions(self):
        # Only admins can create, update, or delete events
        # Normal users can only view events
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def competitions(self, request, slug=None):
        """Get all competitions under this event."""
        event = self.get_object()
        competitions = event.competitions.all()
        serializer = CompetitionListSerializer(competitions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured competition events."""
        events = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def overall_leaderboard(self, request, slug=None):
        """
        Get overall leaderboard aggregating scores from all competitions in this event.
        
        Scoring Logic:
        - Only counts normalized scores (0-100 points per competition)
        - Teams that don't participate in a competition get 0 points for that competition
        - Total score = sum of all normalized scores across competitions
        - Average score = total score / number of competitions in event (not just participated)
        """
        from apps.leaderboard.models import LeaderboardEntry
        from django.db.models import Sum, Count, Avg, Q, F
        from collections import defaultdict
        
        event = self.get_object()
        competitions = event.competitions.all()
        total_competitions = competitions.count()
        
        if not total_competitions:
            return Response({
                'event_id': event.id,
                'event_title': event.title,
                'entries': [],
                'competitions_count': 0
            })
        
        # Get all leaderboard entries for competitions in this event
        all_entries = LeaderboardEntry.objects.filter(
            competition__in=competitions
        ).select_related('competition').order_by('kaggle_team_name', 'competition__title')
        
        # Group entries by team and calculate normalized scores
        team_data = defaultdict(lambda: {
            'scores': [],
            'competitions_participated': 0,
            'competition_details': []
        })
        
        for entry in all_entries:
            team_name = entry.kaggle_team_name or 'Unknown'
            competition = entry.competition
            
            # Calculate normalized score (0-100 scale)
            # If scoring config is properly set, the score should already be normalized
            # But we'll clamp it to 0-100 range for safety
            if competition.points_for_perfect_score > 0:
                # Score is already normalized during sync
                normalized_score = max(0.0, min(competition.points_for_perfect_score, float(entry.score)))
            else:
                # Fallback: use raw score clamped to 0-100
                normalized_score = max(0.0, min(100.0, float(entry.score)))
            
            team_data[team_name]['scores'].append(normalized_score)
            team_data[team_name]['competitions_participated'] += 1
            team_data[team_name]['competition_details'].append({
                'competition_name': competition.title,
                'score': normalized_score,
                'rank': entry.rank
            })
        
        # Calculate final scores for each team
        leaderboard_data = []
        for team_name, data in team_data.items():
            total_score = sum(data['scores'])
            # Average score across ALL competitions in event (treating missing as 0)
            average_score = total_score / total_competitions
            
            leaderboard_data.append({
                'team_name': team_name,
                'total_score': round(total_score, 2),
                'average_score': round(average_score, 2),
                'competitions_participated': data['competitions_participated'],
                'missing_competitions': total_competitions - data['competitions_participated'],
                'competition_details': data['competition_details']
            })
        
        # Sort by total score (descending)
        leaderboard_data.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Assign ranks
        for rank, entry in enumerate(leaderboard_data, 1):
            entry['rank'] = rank
        
        return Response({
            'event_id': event.id,
            'event_title': event.title,
            'entries': leaderboard_data,
            'competitions_count': total_competitions
        })


class CompetitionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Competition CRUD operations.
    """
    queryset = Competition.objects.all().select_related('event')
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

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def fetch_kaggle_leaderboard(self, request, pk=None):
        """
        Fetch and update leaderboard from Kaggle using CSV download method.
        Downloads complete leaderboard (all entries, not just top 20) via Kaggle CLI.
        """
        competition = self.get_object()
        
        if not competition.kaggle_competition_id:
            return Response(
                {'error': 'This competition is not linked to Kaggle'},
                status=400
            )
        
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Starting leaderboard sync for {competition.title} ({competition.kaggle_competition_id})")
        
        # Use the CSV-based sync system (downloads ALL entries)
        from apps.competitions.kaggle_leaderboard_sync import KaggleLeaderboardSync
        
        try:
            sync_service = KaggleLeaderboardSync()
            # Pass the Competition object, not just the kaggle_competition_id string
            result = sync_service.sync_competition_leaderboard(competition)
            
            if not result['success']:
                error_msg = result.get('error', 'Failed to sync leaderboard')
                logger.error(f"Sync failed: {error_msg}")
                return Response(
                    {'error': error_msg},
                    status=500
                )
            
            entries_synced = result.get('entries_processed', 0)
            logger.info(f"Successfully synced {entries_synced} leaderboard entries for {competition.title}")
            
            return Response({
                'success': True,
                'entries_created': entries_synced,
                'message': f'Leaderboard updated with {entries_synced} entries from Kaggle CSV'
            })
            
        except Exception as e:
            logger.error(f"Error syncing Kaggle leaderboard: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to sync leaderboard: {str(e)}'},
                status=500
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def fetch_kaggle_submissions(self, request, pk=None):
        """
        DEPRECATED: Redirects to leaderboard sync.
        The Kaggle API doesn't provide a method to fetch all submissions.
        Use the leaderboard sync instead, which downloads the complete CSV with all entries.
        """
        competition = self.get_object()
        
        if not competition.kaggle_competition_id:
            return Response(
                {'error': 'This competition is not linked to Kaggle'},
                status=400
            )
        
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"fetch_kaggle_submissions called for {competition.title} - redirecting to leaderboard sync")
        
        # Use the leaderboard sync system instead (with CSV download)
        from apps.competitions.kaggle_leaderboard_sync import KaggleLeaderboardSync
        
        try:
            sync_service = KaggleLeaderboardSync()
            result = sync_service.sync_competition_leaderboard(competition.kaggle_competition_id)
            
            if not result['success']:
                return Response(
                    {'error': result.get('error', 'Failed to sync leaderboard')},
                    status=500
                )
            
            # Return success with leaderboard data
            entries_synced = result.get('entries_synced', 0)
            
            logger.info(f"Synced {entries_synced} leaderboard entries for {competition.title}")
            
            return Response({
                'success': True,
                'submissions_created': 0,  # Not creating submissions, just leaderboard
                'leaderboard_updated': entries_synced,
                'message': f'Synced {entries_synced} leaderboard entries from Kaggle CSV'
            })
            
        except Exception as e:
            logger.error(f"Error syncing leaderboard: {str(e)}")
            return Response(
                {'error': f'Failed to fetch submissions from Kaggle. Using leaderboard sync instead: {str(e)}'},
                status=500
            )

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
    
    @action(detail=False, methods=['get'])
    def search_kaggle(self, request):
        """Search for competitions on Kaggle."""
        from apps.submissions.kaggle_service import get_kaggle_service
        
        search_term = request.query_params.get('q', '')
        page = int(request.query_params.get('page', 1))
        
        kaggle_service = get_kaggle_service()
        results = kaggle_service.search_competitions(search_term=search_term, page=page)
        
        if results is None:
            return Response(
                {'error': 'Failed to search Kaggle competitions'},
                status=500
            )
        
        # Check which competitions already exist in our database
        existing_ids = set(Competition.objects.filter(
            kaggle_competition_id__in=[comp['id'] for comp in results]
        ).values_list('kaggle_competition_id', flat=True))
        
        # Mark which competitions are already imported
        for comp in results:
            comp['imported'] = comp['id'] in existing_ids
        
        return Response({
            'results': results,
            'count': len(results),
            'search_term': search_term
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def import_from_kaggle(self, request):
        """Import a competition from Kaggle by ID with scoring parameters."""
        from apps.submissions.kaggle_service import get_kaggle_service
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        
        kaggle_id = request.data.get('kaggle_id')
        event_id = request.data.get('event_id')  # Optional: assign to an event
        
        # Get scoring configuration parameters
        higher_is_better = request.data.get('higher_is_better', True)
        metric_min_value = request.data.get('metric_min_value', 0.0)
        metric_max_value = request.data.get('metric_max_value', 1.0)
        points_for_perfect_score = request.data.get('points_for_perfect_score', 100.0)
        
        # Enhanced logging for debugging
        logger.info(f"Import request received - kaggle_id: {kaggle_id}, event_id: {event_id}")
        logger.info(f"Scoring config - higher_is_better: {higher_is_better}, min: {metric_min_value}, max: {metric_max_value}, points: {points_for_perfect_score}")
        logger.info(f"Request data: {request.data}")
        
        if not kaggle_id:
            logger.error("Missing kaggle_id in request")
            return Response(
                {'error': 'kaggle_id is required', 'received_data': request.data},
                status=400
            )
        
        logger.info(f"Attempting to import competition with ID: {kaggle_id}")
        
        # Extract competition ID from URL if needed
        if 'kaggle.com' in str(kaggle_id):
            # Extract ID from URL like https://www.kaggle.com/competitions/arc-prize-2025
            kaggle_id = str(kaggle_id).rstrip('/').split('/')[-1]
            logger.info(f"Extracted competition ID from URL: {kaggle_id}")
        
        # Check if already exists
        existing_comp = Competition.objects.filter(kaggle_competition_id=kaggle_id).first()
        if existing_comp:
            logger.warning(f"Competition {kaggle_id} already exists (ID: {existing_comp.id})")
            return Response(
                {
                    'error': 'Competition already imported',
                    'competition_id': existing_comp.id,
                    'competition_title': existing_comp.title
                },
                status=400
            )
        
        # Validate event if provided
        event = None
        if event_id:
            try:
                event = CompetitionEvent.objects.get(id=event_id)
            except CompetitionEvent.DoesNotExist:
                return Response(
                    {'error': 'Competition event not found'},
                    status=404
                )
        
        # Fetch from Kaggle
        kaggle_service = get_kaggle_service()
        comp_data = kaggle_service.get_competition_details(kaggle_id)
        
        if not comp_data:
            return Response(
                {'error': 'Competition not found on Kaggle'},
                status=404
            )
        
        # Determine status and dates based on deadline
        from django.utils import timezone
        
        status = 'ongoing'
        start_date = timezone.now()
        end_date = None
        
        if comp_data.get('deadline'):
            try:
                # Parse deadline
                deadline_str = str(comp_data['deadline'])
                if deadline_str and deadline_str.lower() != 'none':
                    # Try parsing the date
                    from dateutil import parser
                    end_date = parser.parse(deadline_str)
                    
                    # Determine status
                    if end_date < timezone.now():
                        status = 'completed'
                        # Set start date to 30 days before end for completed competitions
                        start_date = end_date - timezone.timedelta(days=30)
                    else:
                        status = 'ongoing'
                        # Set start date to 7 days before now for ongoing competitions
                        start_date = timezone.now() - timezone.timedelta(days=7)
            except:
                # If parsing fails, use current date and ongoing status
                start_date = timezone.now()
                end_date = timezone.now() + timezone.timedelta(days=90)
        else:
            # No deadline provided, set to 90 days from now
            end_date = timezone.now() + timezone.timedelta(days=90)
        
        # Validate and convert scoring parameters to float
        try:
            metric_min_value = float(metric_min_value)
            metric_max_value = float(metric_max_value)
            points_for_perfect_score = float(points_for_perfect_score)
            
            # Validate that max > min
            if metric_max_value <= metric_min_value:
                return Response(
                    {'error': 'metric_max_value must be greater than metric_min_value'},
                    status=400
                )
            
            # Validate that points is positive
            if points_for_perfect_score <= 0:
                return Response(
                    {'error': 'points_for_perfect_score must be greater than 0'},
                    status=400
                )
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid scoring parameter values: {str(e)}'},
                status=400
            )
        
        # Create competition in database with scoring configuration
        competition = Competition.objects.create(
            event=event,  # Assign to event if provided
            title=comp_data['title'],
            description=comp_data.get('description', ''),
            kaggle_competition_id=comp_data['id'],
            kaggle_url=comp_data.get('url', f"https://www.kaggle.com/c/{kaggle_id}"),
            start_date=start_date,
            end_date=end_date,
            status=status,
            prize_pool=str(comp_data.get('reward', 'Knowledge')),
            participants_count=comp_data.get('teamCount', 0),
            rating_weight=1.0,
            max_submissions_per_day=5,
            # Scoring configuration
            higher_is_better=higher_is_better,
            metric_min_value=metric_min_value,
            metric_max_value=metric_max_value,
            points_for_perfect_score=points_for_perfect_score
        )
        
        serializer = CompetitionDetailSerializer(competition)
        return Response({
            'message': 'Competition imported successfully',
            'competition': serializer.data
        })
