from django.core.management.base import BaseCommand
from apps.submissions.tasks import fetch_kaggle_leaderboard
from apps.competitions.models import Competition


class Command(BaseCommand):
    help = 'Manually sync Kaggle leaderboard data for a competition'

    def add_arguments(self, parser):
        parser.add_argument(
            'competition_id',
            type=int,
            help='Database ID of the competition to sync'
        )

    def handle(self, *args, **options):
        competition_id = options['competition_id']
        
        try:
            competition = Competition.objects.get(id=competition_id)
            self.stdout.write(f"Syncing leaderboard for: {competition.title}")
            self.stdout.write(f"Kaggle Competition ID: {competition.kaggle_competition_id}")
            
            # Call the task directly (not via Celery)
            result = fetch_kaggle_leaderboard(competition_id)
            
            self.stdout.write(self.style.SUCCESS(f"✅ {result}"))
            
        except Competition.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Competition with ID {competition_id} not found")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error: {str(e)}")
            )
