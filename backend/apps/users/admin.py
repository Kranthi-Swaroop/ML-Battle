from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'elo_rating', 'highest_rating', 'competitions_participated', 'rating_tier']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'kaggle_username']
    ordering = ['-elo_rating']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('ML Competition Info', {
            'fields': ('elo_rating', 'highest_rating', 'competitions_participated', 'kaggle_username', 'bio', 'avatar_url')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'kaggle_username')
        }),
    )
