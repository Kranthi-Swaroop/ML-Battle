from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/leaderboard/(?P<competition_id>\d+)/$', consumers.LeaderboardConsumer.as_asgi()),
]
