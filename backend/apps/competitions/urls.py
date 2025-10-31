from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetitionViewSet

router = DefaultRouter()
router.register(r'', CompetitionViewSet, basename='competition')

urlpatterns = [
    path('', include(router.urls)),
]
