import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class LeaderboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time leaderboard updates.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.competition_id = self.scope['url_route']['kwargs']['competition_id']
        self.room_group_name = f'leaderboard_{self.competition_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial leaderboard data
        leaderboard_data = await self.get_leaderboard_data()
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_init',
            'data': leaderboard_data
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'refresh':
            # Send updated leaderboard data
            leaderboard_data = await self.get_leaderboard_data()
            await self.send(text_data=json.dumps({
                'type': 'leaderboard_update',
                'data': leaderboard_data
            }))
    
    async def leaderboard_update(self, event):
        """Receive leaderboard update from room group."""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_update',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_leaderboard_data(self):
        """Fetch leaderboard data from database."""
        from .models import LeaderboardEntry
        from .serializers import LeaderboardEntrySerializer
        
        entries = LeaderboardEntry.objects.filter(
            competition_id=self.competition_id
        ).select_related('user').order_by('rank')[:100]  # Top 100
        
        serializer = LeaderboardEntrySerializer(entries, many=True)
        return {
            'competition_id': self.competition_id,
            'entries': serializer.data,
            'updated_at': timezone.now().isoformat()
        }


# Helper function to send updates from outside the consumer
def send_leaderboard_update(competition_id):
    """
    Send leaderboard update to WebSocket group.
    Called from Celery tasks.
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from .models import LeaderboardEntry
    from .serializers import LeaderboardEntrySerializer
    
    channel_layer = get_channel_layer()
    
    # Fetch updated leaderboard data
    entries = LeaderboardEntry.objects.filter(
        competition_id=competition_id
    ).select_related('user').order_by('rank')[:100]
    
    serializer = LeaderboardEntrySerializer(entries, many=True)
    
    data = {
        'competition_id': competition_id,
        'entries': serializer.data,
        'updated_at': timezone.now().isoformat()
    }
    
    # Send to group
    async_to_sync(channel_layer.group_send)(
        f'leaderboard_{competition_id}',
        {
            'type': 'leaderboard_update',
            'data': data
        }
    )
