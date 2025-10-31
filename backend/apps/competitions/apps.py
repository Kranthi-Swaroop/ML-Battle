from django.apps import AppConfig


class CompetitionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.competitions'
    label = 'competitions'
    
    def ready(self):
        """
        Import signals when app is ready.
        This enables automatic Kaggle leaderboard sync on competition create/update.
        """
        import apps.competitions.signals  # noqa
