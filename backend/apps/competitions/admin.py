from django.contrib import admin
from .models import Competition, CompetitionEvent


@admin.register(CompetitionEvent)
class CompetitionEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'status', 'start_date', 'end_date', 'is_featured', 'competition_count']
    list_filter = ['status', 'is_featured', 'start_date']
    search_fields = ['title', 'organizer']
    ordering = ['-start_date']
    readonly_fields = ['slug', 'participants_count', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'banner_image', 'organizer')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Configuration', {
            'fields': ('total_prize_pool', 'is_featured', 'participants_count')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'kaggle_competition_id', 'status', 'start_date', 'end_date', 'participants_count']
    list_filter = ['status', 'event', 'start_date']
    search_fields = ['title', 'kaggle_competition_id']
    ordering = ['-start_date']
    readonly_fields = ['participants_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Event Assignment', {
            'fields': ('event',)
        }),
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
