"""
URL configuration for MLBattle project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Routes
    path('api/users/', include('apps.users.urls')),
    path('api/competitions/', include('apps.competitions.urls')),
    path('api/submissions/', include('apps.submissions.urls')),
    path('api/leaderboard/', include('apps.leaderboard.urls')),
    path('api/ratings/', include('apps.ratings.urls')),
]
