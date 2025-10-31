"""
ELO Rating System Calculator
"""
import math
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class EloRatingSystem:
    """
    ELO Rating System implementation for ML competitions.
    """
    
    @staticmethod
    def calculate_k_factor(total_participants: int) -> float:
        """
        Calculate dynamic K-factor based on competition size.
        
        Args:
            total_participants: Total number of participants in the competition
            
        Returns:
            K-factor value
        """
        if total_participants < 2:
            return 16
        
        k = math.log2(total_participants) * 8
        return min(64, max(16, k))
    
    @staticmethod
    def calculate_expected_score(player_rating: float, opponent_rating: float) -> float:
        """
        Calculate expected score using ELO formula.
        
        Args:
            player_rating: Current player rating
            opponent_rating: Average opponent rating
            
        Returns:
            Expected score (0 to 1)
        """
        return 1 / (1 + math.pow(10, (opponent_rating - player_rating) / 400))
    
    @staticmethod
    def calculate_actual_score(rank: int, total_participants: int) -> float:
        """
        Calculate actual performance score based on rank.
        Higher rank (lower number) = higher score
        
        Args:
            rank: Player's rank in competition (1 = best)
            total_participants: Total number of participants
            
        Returns:
            Actual score (0 to 1)
        """
        if total_participants <= 1:
            return 1.0
        
        # Normalize rank to score between 0 and 1
        # Rank 1 -> Score 1.0, Last rank -> Score 0.0
        return 1 - ((rank - 1) / (total_participants - 1))
    
    @staticmethod
    def calculate_new_rating(
        old_rating: int,
        actual_score: float,
        expected_score: float,
        k_factor: float,
        rating_weight: float = 1.0
    ) -> int:
        """
        Calculate new rating using ELO formula.
        
        Args:
            old_rating: Current player rating
            actual_score: Actual performance score
            expected_score: Expected performance score
            k_factor: K-factor for this competition
            rating_weight: Competition weight multiplier
            
        Returns:
            New rating
        """
        rating_change = k_factor * rating_weight * (actual_score - expected_score)
        new_rating = old_rating + round(rating_change)
        
        # Ensure rating doesn't go below minimum
        return max(0, new_rating)
    
    @staticmethod
    def calculate_competition_ratings(
        participants: List[Dict],
        competition_weight: float = 1.0
    ) -> List[Dict]:
        """
        Calculate ratings for all participants in a competition.
        
        Args:
            participants: List of dicts with keys: user_id, username, old_rating, rank
            competition_weight: Weight/importance of this competition
            
        Returns:
            List of dicts with rating changes
        """
        total_participants = len(participants)
        
        if total_participants == 0:
            logger.warning("No participants to calculate ratings for")
            return []
        
        # Calculate K-factor based on competition size
        k_factor = EloRatingSystem.calculate_k_factor(total_participants)
        
        # Calculate average rating of all participants (opponent pool)
        avg_rating = sum(p['old_rating'] for p in participants) / total_participants
        
        results = []
        
        for participant in participants:
            old_rating = participant['old_rating']
            rank = participant['rank']
            
            # Calculate expected score
            expected_score = EloRatingSystem.calculate_expected_score(
                old_rating, avg_rating
            )
            
            # Calculate actual score based on rank
            actual_score = EloRatingSystem.calculate_actual_score(
                rank, total_participants
            )
            
            # Calculate new rating
            new_rating = EloRatingSystem.calculate_new_rating(
                old_rating,
                actual_score,
                expected_score,
                k_factor,
                competition_weight
            )
            
            rating_change = new_rating - old_rating
            
            results.append({
                'user_id': participant['user_id'],
                'username': participant['username'],
                'old_rating': old_rating,
                'new_rating': new_rating,
                'rating_change': rating_change,
                'rank': rank,
                'actual_score': actual_score,
                'expected_score': expected_score,
            })
            
            logger.debug(
                f"{participant['username']}: Rank {rank}, "
                f"{old_rating} -> {new_rating} ({rating_change:+d})"
            )
        
        logger.info(
            f"Calculated ratings for {total_participants} participants "
            f"(K-factor: {k_factor:.2f})"
        )
        
        return results
