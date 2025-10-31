from django.contrib import admin
from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'competition', 'score', 'status', 'submission_time']
    list_filter = ['status', 'competition', 'submission_time']
    search_fields = ['user__username', 'competition__title', 'kaggle_submission_id']
    ordering = ['-submission_time']
    readonly_fields = ['submission_time']
    
    def has_add_permission(self, request):
        # Submissions come from Kaggle, so disable manual creation
        return False
