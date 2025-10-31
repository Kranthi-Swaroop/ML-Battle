"""
Kaggle API Integration Service
"""
import os
import logging
from typing import Optional, Dict, List
from kaggle.api.kaggle_api_extended import KaggleApi
from django.conf import settings

logger = logging.getLogger(__name__)


class KaggleService:
    """
    Service class for interacting with Kaggle API.
    """
    
    def __init__(self):
        self.api = KaggleApi()
        self._authenticated = False
        
    def authenticate(self):
        """Authenticate with Kaggle API."""
        try:
            # Set credentials from settings
            if settings.KAGGLE_USERNAME and settings.KAGGLE_KEY:
                os.environ['KAGGLE_USERNAME'] = settings.KAGGLE_USERNAME
                os.environ['KAGGLE_KEY'] = settings.KAGGLE_KEY
            
            self.api.authenticate()
            self._authenticated = True
            logger.info("Successfully authenticated with Kaggle API")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Kaggle API: {str(e)}")
            return False
    
    def get_competition_leaderboard(self, competition_id: str) -> Optional[List[Dict]]:
        """
        Fetch leaderboard data for a specific competition.
        
        Args:
            competition_id: Kaggle competition identifier
            
        Returns:
            List of leaderboard entries or None if failed
        """
        if not self._authenticated:
            if not self.authenticate():
                return None
        
        try:
            # Fetch leaderboard from Kaggle
            leaderboard = self.api.competition_leaderboard_view(competition_id)
            
            # Parse leaderboard data
            entries = []
            for i, entry in enumerate(leaderboard, start=1):
                entries.append({
                    'rank': i,
                    'team_name': entry.teamName,
                    'score': entry.score,
                    'submissions': entry.submissionDate if hasattr(entry, 'submissionDate') else None,
                })
            
            logger.info(f"Fetched {len(entries)} leaderboard entries for {competition_id}")
            return entries
            
        except Exception as e:
            logger.error(f"Failed to fetch leaderboard for {competition_id}: {str(e)}")
            return None
    
    def get_competition_submissions(self, competition_id: str) -> Optional[List[Dict]]:
        """
        Fetch user's submissions for a specific competition.
        
        Args:
            competition_id: Kaggle competition identifier
            
        Returns:
            List of submission data or None if failed
        """
        if not self._authenticated:
            if not self.authenticate():
                return None
        
        try:
            submissions = self.api.competition_submissions(competition_id)
            
            submission_list = []
            for sub in submissions:
                submission_list.append({
                    'ref': sub.ref,
                    'date': sub.date,
                    'description': sub.description,
                    'status': sub.status,
                    'publicScore': sub.publicScore if hasattr(sub, 'publicScore') else None,
                    'privateScore': sub.privateScore if hasattr(sub, 'privateScore') else None,
                })
            
            logger.info(f"Fetched {len(submission_list)} submissions for {competition_id}")
            return submission_list
            
        except Exception as e:
            logger.error(f"Failed to fetch submissions for {competition_id}: {str(e)}")
            return None
    
    def get_competition_details(self, competition_id: str) -> Optional[Dict]:
        """
        Fetch competition details from Kaggle.
        
        Args:
            competition_id: Kaggle competition identifier
            
        Returns:
            Competition details dict or None if failed
        """
        if not self._authenticated:
            if not self.authenticate():
                return None
        
        try:
            competitions = self.api.competition_list(search=competition_id)
            
            for comp in competitions:
                if comp.ref == competition_id:
                    return {
                        'id': comp.ref,
                        'title': comp.title,
                        'description': comp.description,
                        'url': comp.url,
                        'deadline': comp.deadline,
                        'category': comp.category,
                        'reward': comp.reward,
                        'teamCount': comp.teamCount,
                        'userHasEntered': comp.userHasEntered,
                    }
            
            logger.warning(f"Competition {competition_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch competition details for {competition_id}: {str(e)}")
            return None


# Singleton instance
_kaggle_service = None

def get_kaggle_service() -> KaggleService:
    """Get or create Kaggle service instance."""
    global _kaggle_service
    if _kaggle_service is None:
        _kaggle_service = KaggleService()
    return _kaggle_service
