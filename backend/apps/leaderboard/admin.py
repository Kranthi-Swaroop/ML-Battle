from django.contrib import admin
from .models import LeaderboardEntry


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'competition', 'rank', 'best_score', 'submissions_count', 'last_submission_time']
    list_filter = ['competition']
    search_fields = ['user__username', 'competition__title']
    ordering = ['competition', 'rank']
    readonly_fields = ['last_submission_time']
