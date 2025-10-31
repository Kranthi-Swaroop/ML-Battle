"""
Automated Kaggle Leaderboard Sync Service
- Downloads complete leaderboard from Kaggle using CLI (ALL entries, not just 20)
- Saves to temporary CSV
- Updates database
- Deletes CSV to save space
- Runs automatically every 5 minutes via Celery

Requirements: Kaggle 1.7.4.5+ for --download flag to work
"""
import os
import subprocess
import time
import pandas as pd
from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class KaggleLeaderboardSync:
    """Service to sync Kaggle leaderboard with local database"""
    
    def __init__(self):
        self.api = KaggleApi()
        self.api.authenticate()
        self.temp_dir = os.path.join(settings.BASE_DIR, 'temp_kaggle_data')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def fetch_and_save_to_csv(self, competition_slug):
        """
        Download complete leaderboard CSV using Kaggle CLI (gets ALL entries, not just top 20)
        
        Requires: Kaggle 1.7.4.5+ for --download flag to work properly
        
        Returns:
            str: Path to the CSV file
        """
        import zipfile
        import shutil
        
        logger.info(f"Downloading full leaderboard for: {competition_slug}")
        
        try:
            # Create unique download directory
            download_path = os.path.join(self.temp_dir, f"{competition_slug}_{int(time.time())}")
            os.makedirs(download_path, exist_ok=True)
            
            # Execute kaggle CLI to download complete leaderboard
            # Use full path to kaggle executable in virtual environment (Windows compatibility)
            import sys
            kaggle_exe = os.path.join(os.path.dirname(sys.executable), 'kaggle.exe')
            if not os.path.exists(kaggle_exe):
                # Try without .exe for Unix systems
                kaggle_exe = os.path.join(os.path.dirname(sys.executable), 'kaggle')
            
            logger.info(f"Running: {kaggle_exe} competitions leaderboard {competition_slug} --download")
            result = subprocess.run(
                [kaggle_exe, 'competitions', 'leaderboard', competition_slug, '--download', '--path', download_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout
            )
            
            # Find and extract ZIP file
            zip_files = [f for f in os.listdir(download_path) if f.endswith('.zip')]
            if not zip_files:
                logger.error(f"No ZIP file found in {download_path}")
                return None
            
            zip_path = os.path.join(download_path, zip_files[0])
            logger.info(f"Extracting {zip_files[0]}...")
            
            # Extract CSV from ZIP
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(download_path)
            
            # Find extracted CSV (handle Windows path issues with colons in filename)
            csv_files = [f for f in os.listdir(download_path) if f.endswith('.csv')]
            if not csv_files:
                logger.error(f"No CSV file found after extraction in {download_path}")
                return None
            
            csv_file = csv_files[0]
            csv_path = os.path.join(download_path, csv_file)
            
            # Rename CSV if it has colons (Windows path issue with ISO timestamp)
            if ':' in csv_file:
                new_name = csv_file.replace(':', '_').replace('T', '_T_')
                new_path = os.path.join(download_path, new_name)
                shutil.move(csv_path, new_path)
                csv_path = new_path
                logger.info(f"Renamed CSV to avoid Windows path issues: {new_name}")
            
            # Clean up ZIP file
            os.remove(zip_path)
            
            # Count entries for logging
            df = pd.read_csv(csv_path)
            logger.info(f"✅ Downloaded complete leaderboard: {len(df)} entries")
            
            return csv_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Kaggle CLI error: {e.stderr}")
            return None
        except subprocess.TimeoutExpired:
            logger.error(f"Download timeout for {competition_slug}")
            return None
        except Exception as e:
            logger.error(f"Error downloading leaderboard: {e}")
            return None
    
    def calculate_normalized_score(self, value, competition):
        """
        Calculate normalized score based on competition's scoring configuration.
        
        Formula:
        - If higher is better: (value - min) / (max - min) * PS_points
        - If lower is better: (max - value) / (max - min) * PS_points
        
        Args:
            value: Raw metric value from Kaggle (float)
            competition: Competition object with scoring configuration
        
        Returns:
            float: Normalized score (0 to PS_points)
        """
        try:
            value = float(value)
            min_val = float(competition.metric_min_value)
            max_val = float(competition.metric_max_value)
            ps_points = float(competition.points_for_perfect_score)
            
            # Avoid division by zero
            if max_val == min_val:
                logger.warning(f"Min and max values are equal ({min_val}), returning 0")
                return 0.0
            
            if competition.higher_is_better:
                # Higher is better: (value - min) / (max - min) * PS_points
                normalized = ((value - min_val) / (max_val - min_val)) * ps_points
            else:
                # Lower is better: (max - value) / (max - min) * PS_points
                normalized = ((max_val - value) / (max_val - min_val)) * ps_points
            
            # Clamp between 0 and PS_points
            normalized = max(0.0, min(ps_points, normalized))
            
            return normalized
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating normalized score: {e}")
            return 0.0
    
    def process_csv_and_update_db(self, csv_path, competition):
        """
        Read CSV and update database with leaderboard entries
        
        CSV Format from Kaggle: Rank, TeamId, TeamName, LastSubmissionDate, Score, SubmissionCount, TeamMemberUserNames
        
        Args:
            csv_path: Path to the CSV file
            competition: Competition object from database
        """
        from apps.leaderboard.models import LeaderboardEntry
        from apps.users.models import User
        
        logger.info(f"Processing CSV: {csv_path}")
        logger.info(f"Scoring config - Higher is better: {competition.higher_is_better}, "
                   f"Min: {competition.metric_min_value}, Max: {competition.metric_max_value}, "
                   f"PS Points: {competition.points_for_perfect_score}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"CSV has {len(df)} entries with columns: {df.columns.tolist()}")
            
            updated_count = 0
            created_count = 0
            skipped_count = 0
            
            # Process each entry
            for _, row in df.iterrows():
                # Use actual Kaggle CSV column names
                team_name = row['TeamName']
                rank = row['Rank']
                raw_score = float(row['Score'])  # Raw score from Kaggle
                submission_date = row.get('LastSubmissionDate')
                team_usernames = row.get('TeamMemberUserNames', '')
                
                # Calculate normalized score using competition's scoring configuration
                normalized_score = self.calculate_normalized_score(raw_score, competition)
                logger.debug(f"{team_name}: Raw score {raw_score} -> Normalized {normalized_score:.4f}")
                
                # Try to find matching user by username
                # First try team member usernames, then team name
                user = None
                
                if pd.notna(team_usernames) and team_usernames:
                    # Try each team member username
                    for username in str(team_usernames).split(','):
                        username = username.strip()
                        try:
                            user = User.objects.get(username=username)
                            break
                        except User.DoesNotExist:
                            continue
                
                # If no user found by team members, try team name
                if not user:
                    try:
                        user = User.objects.get(username=team_name)
                    except User.DoesNotExist:
                        # For public Kaggle competitions, create entry without user
                        # This allows displaying the full leaderboard even for non-registered users
                        logger.debug(f"Creating Kaggle-only entry for team: {team_name}")
                        pass
                
                # Update or create leaderboard entry
                # For public competitions, use kaggle_team_name as unique identifier if user is None
                if user:
                    entry, created = LeaderboardEntry.objects.update_or_create(
                        competition=competition,
                        user=user,
                        defaults={
                            'score': normalized_score,  # Use normalized score
                            'rank': rank,
                            'kaggle_team_name': team_name,
                            'submission_date': pd.to_datetime(submission_date) if pd.notna(submission_date) else None
                        }
                    )
                else:
                    # For Kaggle-only participants (not registered on our platform)
                    entry, created = LeaderboardEntry.objects.update_or_create(
                        competition=competition,
                        user__isnull=True,
                        kaggle_team_name=team_name,
                        defaults={
                            'score': normalized_score,  # Use normalized score
                            'rank': rank,
                            'submission_date': pd.to_datetime(submission_date) if pd.notna(submission_date) else None
                        }
                    )
                
                if created:
                    created_count += 1
                    logger.debug(f"Created entry for {team_name} - Rank: {rank}, Raw: {raw_score}, Normalized: {normalized_score:.4f}")
                else:
                    updated_count += 1
                    logger.debug(f"Updated entry for {team_name} - Rank: {rank}, Raw: {raw_score}, Normalized: {normalized_score:.4f}")
            
            logger.info(f"✅ Database update complete - Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}")
            return created_count + updated_count
            
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            return 0
    
    def cleanup_csv(self, csv_path):
        """Delete the temporary CSV file"""
        try:
            if os.path.exists(csv_path):
                os.remove(csv_path)
                logger.info(f"Deleted temporary file: {csv_path}")
                return True
        except Exception as e:
            logger.error(f"Error deleting file {csv_path}: {e}")
        return False
    
    def cleanup_old_files(self):
        """Delete all old CSV files in temp directory"""
        try:
            if os.path.exists(self.temp_dir):
                files = os.listdir(self.temp_dir)
                for file in files:
                    if file.endswith('.csv'):
                        file_path = os.path.join(self.temp_dir, file)
                        os.remove(file_path)
                        logger.info(f"Cleaned up old file: {file}")
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
    
    def sync_competition_leaderboard(self, competition):
        """
        Complete sync process for a competition:
        1. Fetch from Kaggle
        2. Save to CSV
        3. Update database
        4. Delete CSV
        
        Args:
            competition: Competition object with kaggle_competition_id
        
        Returns:
            dict: Sync results
        """
        logger.info(f"Starting leaderboard sync for: {competition.title}")
        
        result = {
            'success': False,
            'competition': competition.title,
            'entries_processed': 0,
            'error': None
        }
        
        try:
            # Extract competition slug from URL if needed
            kaggle_id = competition.kaggle_competition_id
            if kaggle_id.startswith('http'):
                # Extract slug from URL: https://www.kaggle.com/competitions/slug -> slug
                kaggle_id = kaggle_id.rstrip('/').split('/')[-1]
            
            logger.info(f"Using Kaggle competition slug: {kaggle_id}")
            
            # Step 1: Fetch and save to CSV
            csv_path = self.fetch_and_save_to_csv(kaggle_id)
            
            if not csv_path:
                result['error'] = "Failed to fetch leaderboard"
                return result
            
            # Step 2: Process CSV and update database
            entries_processed = self.process_csv_and_update_db(csv_path, competition)
            result['entries_processed'] = entries_processed
            
            # Step 3: Delete CSV
            self.cleanup_csv(csv_path)
            
            result['success'] = True
            logger.info(f"Sync completed successfully for {competition.title}")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Sync failed for {competition.title}: {e}")
        
        return result


# Standalone function for testing
def sync_single_competition(competition_slug, competition_id):
    """Test function to sync a single competition"""
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    django.setup()
    
    from apps.competitions.models import Competition
    
    try:
        competition = Competition.objects.get(id=competition_id)
        
        syncer = KaggleLeaderboardSync()
        result = syncer.sync_competition_leaderboard(competition)
        
        print(f"\n{'='*100}")
        print("SYNC RESULTS:")
        print(f"{'='*100}")
        print(f"Competition: {result['competition']}")
        print(f"Success: {result['success']}")
        print(f"Entries Processed: {result['entries_processed']}")
        if result['error']:
            print(f"Error: {result['error']}")
        print(f"{'='*100}\n")
        
        return result
        
    except Competition.DoesNotExist:
        print(f"Competition with ID {competition_id} not found")
        return None


if __name__ == "__main__":
    # Test the sync
    print("Testing Kaggle Leaderboard Sync...")
    # Replace with actual competition ID from your database
    sync_single_competition("spaceship-titanic", 1)
