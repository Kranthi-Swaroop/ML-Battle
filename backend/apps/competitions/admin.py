from django.contrib import admin
from .models import Competition


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'kaggle_competition_id', 'status', 'start_date', 'end_date', 'participants_count']
    list_filter = ['status', 'start_date']
    search_fields = ['title', 'kaggle_competition_id']
    ordering = ['-start_date']
    readonly_fields = ['participants_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'kaggle_competition_id', 'kaggle_url')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Configuration', {
            'fields': ('rating_weight', 'max_submissions_per_day', 'evaluation_metric', 'prize_pool')
        }),
        ('Statistics', {
            'fields': ('participants_count', 'created_at', 'updated_at')
        }),
    )
