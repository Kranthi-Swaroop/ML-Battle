from django.contrib import admin
from .models import RatingHistory


@admin.register(RatingHistory)
class RatingHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'competition', 'old_rating', 'new_rating', 'rating_change', 'rank', 'timestamp']
    list_filter = ['competition', 'timestamp']
    search_fields = ['user__username', 'competition__title']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    def has_add_permission(self, request):
        # Rating history is created automatically
        return False
