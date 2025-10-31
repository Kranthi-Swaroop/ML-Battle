from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RatingHistoryViewSet

router = DefaultRouter()
router.register(r'', RatingHistoryViewSet, basename='rating-history')

urlpatterns = [
    path('', include(router.urls)),
]
