"""
Simple script to fetch and display Kaggle leaderboard using working API
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd

def fetch_leaderboard(competition_slug):
    """Fetch and display leaderboard"""
    
    # Initialize API
    api = KaggleApi()
    api.authenticate()
    
    print(f"\nFetching leaderboard for: {competition_slug}")
    print("="*80)
    
    try:
        # Method 1: Try to get all competition submissions
        print("\nAttempting to fetch competition leaderboard...")
        
        result = api.competition_leaderboard_view(competition_slug)
        
        # Check what we got back
        print(f"Result type: {type(result)}")
        
        # Result is a list of submissions
        submissions = result
        print(f"\nFound {len(submissions)} leaderboard entries")
        
        # Create list for dataframe
        data = []
        
        print(f"\n{'='*80}")
        print(f"{'Rank':<8} {'Team Name':<40} {'Score':<15} {'Submissions':<12}")
        print("="*80)
        
        for sub in submissions[:50]:  # Display top 50
            rank = sub.rank if hasattr(sub, 'rank') else 'N/A'
            team = sub.teamName if hasattr(sub, 'teamName') else 'Unknown'
            score = sub.score if hasattr(sub, 'score') else 'N/A'
            count = sub.submittedCount if hasattr(sub, 'submittedCount') else 'N/A'
            
            # Truncate long team names
            display_team = team[:38] + '..' if len(team) > 40 else team
            
            print(f"{str(rank):<8} {display_team:<40} {str(score):<15} {str(count):<12}")
            
            data.append({
                'Rank': rank,
                'TeamId': sub.teamId if hasattr(sub, 'teamId') else None,
                'TeamName': team,
                'Score': score,
                'SubmittedCount': count,
                'SubmissionDate': sub.submissionDate if hasattr(sub, 'submissionDate') else None
            })
        
        print("="*80)
        print(f"\nTotal entries displayed: {len(data)}")
        
        # Save to CSV
        if data:
            df = pd.DataFrame(data)
            csv_path = f'temp_leaderboard/{competition_slug}_leaderboard.csv'
            os.makedirs('temp_leaderboard', exist_ok=True)
            df.to_csv(csv_path, index=False)
            print(f"\n✅ Leaderboard saved to: {csv_path}")
            
            # Display statistics
            print(f"\n{'='*80}")
            print("STATISTICS:")
            print(f"{'='*80}")
            if 'Score' in df.columns:
                scores = pd.to_numeric(df['Score'], errors='coerce')
                print(f"Top Score: {scores.max()}")
                print(f"Average Score: {scores.mean():.6f}")
                print(f"Median Score: {scores.median():.6f}")
            print(f"{'='*80}\n")
            
            return df
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e)}")
        
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
    
    return None


if __name__ == "__main__":
    competition = "spaceship-titanic"
    df = fetch_leaderboard(competition)
    
    if df is not None:
        print("\n✅ SUCCESS: Leaderboard fetched and displayed!")
    else:
        print("\n❌ FAILED: Could not fetch leaderboard")
