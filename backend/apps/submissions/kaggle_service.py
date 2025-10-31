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
    
    def get_all_competition_submissions(self, competition_id: str) -> Optional[List[Dict]]:
        """
        Fetch all submissions from the leaderboard for a specific competition.
        This fetches submission data for all participants from the public leaderboard.
        
        Args:
            competition_id: Kaggle competition identifier
            
        Returns:
            List of submission data with team names and scores or None if failed
        """
        if not self._authenticated:
            if not self.authenticate():
                return None
        
        try:
            # Fetch leaderboard which contains submission information
            leaderboard = self.api.competition_leaderboard_view(competition_id)
            
            submission_list = []
            for entry in leaderboard:
                submission_data = {
                    'team_name': entry.teamName,
                    'team_id': entry.teamId if hasattr(entry, 'teamId') else None,
                    'score': entry.score,
                    'submission_date': entry.submissionDate if hasattr(entry, 'submissionDate') else None,
                }
                submission_list.append(submission_data)
            
            logger.info(f"Fetched {len(submission_list)} submissions from leaderboard for {competition_id}")
            return submission_list
            
        except Exception as e:
            logger.error(f"Failed to fetch all submissions for {competition_id}: {str(e)}")
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
            # First try to get competition directly by ID
            try:
                comp = self.api.competition_view(competition_id)
                return {
                    'id': comp.ref if hasattr(comp, 'ref') else competition_id,
                    'title': comp.title if hasattr(comp, 'title') else competition_id,
                    'description': comp.description if hasattr(comp, 'description') else '',
                    'url': comp.url if hasattr(comp, 'url') else f"https://www.kaggle.com/c/{competition_id}",
                    'deadline': str(comp.deadline) if hasattr(comp, 'deadline') and comp.deadline else None,
                    'category': comp.category if hasattr(comp, 'category') else 'general',
                    'reward': str(comp.reward) if hasattr(comp, 'reward') else 'Knowledge',
                    'teamCount': comp.teamCount if hasattr(comp, 'teamCount') else 0,
                    'userHasEntered': comp.userHasEntered if hasattr(comp, 'userHasEntered') else False,
                }
            except:
                # If direct fetch fails, search for it
                competitions = self.api.competitions_list(search=competition_id)
                
                # Try exact match first
                for comp in competitions:
                    if comp.ref == competition_id:
                        return {
                            'id': comp.ref,
                            'title': comp.title,
                            'description': comp.description if hasattr(comp, 'description') else '',
                            'url': comp.url,
                            'deadline': str(comp.deadline) if hasattr(comp, 'deadline') and comp.deadline else None,
                            'category': comp.category if hasattr(comp, 'category') else 'general',
                            'reward': str(comp.reward) if hasattr(comp, 'reward') else 'Knowledge',
                            'teamCount': comp.teamCount if hasattr(comp, 'teamCount') else 0,
                            'userHasEntered': comp.userHasEntered if hasattr(comp, 'userHasEntered') else False,
                        }
                
                # If no exact match, return first result if available
                if competitions:
                    comp = competitions[0]
                    return {
                        'id': comp.ref,
                        'title': comp.title,
                        'description': comp.description if hasattr(comp, 'description') else '',
                        'url': comp.url,
                        'deadline': str(comp.deadline) if hasattr(comp, 'deadline') and comp.deadline else None,
                        'category': comp.category if hasattr(comp, 'category') else 'general',
                        'reward': str(comp.reward) if hasattr(comp, 'reward') else 'Knowledge',
                        'teamCount': comp.teamCount if hasattr(comp, 'teamCount') else 0,
                        'userHasEntered': comp.userHasEntered if hasattr(comp, 'userHasEntered') else False,
                    }
            
            logger.warning(f"Competition {competition_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch competition details for {competition_id}: {str(e)}")
            return None
    
    def search_competitions(self, search_term: str = '', page: int = 1, page_size: int = 20) -> Optional[List[Dict]]:
        """
        Search for competitions on Kaggle.
        
        Args:
            search_term: Search query string
            page: Page number for pagination
            page_size: Number of results per page
            
        Returns:
            List of competition dicts or None if failed
        """
        if not self._authenticated:
            if not self.authenticate():
                return None
        
        try:
            competitions = self.api.competitions_list(search=search_term, page=page)
            
            results = []
            for comp in competitions[:page_size]:
                # Convert tags to list of strings if they exist
                tags = []
                if hasattr(comp, 'tags') and comp.tags:
                    tags = [str(tag) for tag in comp.tags]
                
                results.append({
                    'id': comp.ref,
                    'title': comp.title,
                    'description': comp.description if hasattr(comp, 'description') else '',
                    'url': comp.url,
                    'deadline': str(comp.deadline) if hasattr(comp, 'deadline') and comp.deadline else None,
                    'category': comp.category if hasattr(comp, 'category') else 'general',
                    'reward': str(comp.reward) if hasattr(comp, 'reward') else 'Knowledge',
                    'teamCount': comp.teamCount if hasattr(comp, 'teamCount') else 0,
                    'userHasEntered': comp.userHasEntered if hasattr(comp, 'userHasEntered') else False,
                    'tags': tags,
                })
            
            logger.info(f"Found {len(results)} competitions for search term: {search_term}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search competitions: {str(e)}")
            return None
    
    def competitions_list(self, page: int = 1) -> Optional[List[Dict]]:
        """
        Get list of all available Kaggle competitions.
        
        Args:
            page: Page number for pagination
            
        Returns:
            List of competition dicts or None if failed
        """
        return self.search_competitions(search_term='', page=page)


# Singleton instance
_kaggle_service = None

def get_kaggle_service() -> KaggleService:
    """Get or create Kaggle service instance."""
    global _kaggle_service
    if _kaggle_service is None:
        _kaggle_service = KaggleService()
    return _kaggle_service
