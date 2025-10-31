"""
Enhanced script to display full Kaggle leaderboard data
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd

def display_full_leaderboard(competition_slug):
    """Fetch and display complete leaderboard with all details"""
    
    # Initialize API
    api = KaggleApi()
    api.authenticate()
    
    print(f"\n{'='*100}")
    print(f"KAGGLE COMPETITION LEADERBOARD: {competition_slug.upper()}")
    print(f"{'='*100}\n")
    
    try:
        # Fetch leaderboard
        submissions = api.competition_leaderboard_view(competition_slug)
        
        print(f"✅ Successfully fetched {len(submissions)} leaderboard entries\n")
        
        # First, check what attributes are available
        if submissions:
            print("Available attributes in submission object:")
            print(dir(submissions[0]))
            print()
        
        # Create data list
        data = []
        
        # Display header
        print(f"{'#':<6} {'Team Name':<45} {'Score':<15} {'Submitted':<12}")
        print("="*100)
        
        # Process all submissions
        for idx, sub in enumerate(submissions, 1):
            # Get attributes safely
            team = getattr(sub, 'teamName', 'Unknown')
            score = getattr(sub, 'score', 'N/A')
            submitted_count = getattr(sub, 'submittedCount', 'N/A')
            team_id = getattr(sub, 'teamId', None)
            submission_date = getattr(sub, 'submissionDate', None)
            
            # Truncate long team names for display
            display_team = team[:43] + '..' if len(team) > 45 else team
            
            # Display row
            print(f"{idx:<6} {display_team:<45} {str(score):<15} {str(submitted_count):<12}")
            
            # Add to data list
            data.append({
                'Rank': idx,
                'TeamId': team_id,
                'TeamName': team,
                'Score': score,
                'SubmittedCount': submitted_count,
                'SubmissionDate': submission_date
            })
        
        print("="*100)
        print(f"\nTotal entries: {len(data)}\n")
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        os.makedirs('temp_leaderboard', exist_ok=True)
        csv_path = f'temp_leaderboard/{competition_slug}_full_leaderboard.csv'
        df.to_csv(csv_path, index=False)
        
        print(f"{'='*100}")
        print("STATISTICS:")
        print(f"{'='*100}")
        
        if 'Score' in df.columns:
            scores = pd.to_numeric(df['Score'], errors='coerce')
            print(f"🏆 Top Score:        {scores.max():.6f}")
            print(f"📊 Average Score:    {scores.mean():.6f}")
            print(f"📈 Median Score:     {scores.median():.6f}")
            print(f"📉 Lowest Score:     {scores.min():.6f}")
            print(f"📏 Std Deviation:    {scores.std():.6f}")
        
        print(f"\n💾 Full leaderboard saved to: {csv_path}")
        print(f"{'='*100}\n")
        
        # Display top 10
        print(f"{'='*100}")
        print("TOP 10 TEAMS:")
        print(f"{'='*100}\n")
        
        top_10 = df.head(10)
        for idx, row in top_10.iterrows():
            print(f"#{row['Rank']:<4} {row['TeamName']:<50} Score: {row['Score']}")
        
        print(f"\n{'='*100}\n")
        
        return df
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    competition = "spaceship-titanic"
    df = display_full_leaderboard(competition)
    
    if df is not None:
        print("✅ SUCCESS: Leaderboard fetched, displayed, and saved!")
    else:
        print("❌ FAILED: Could not fetch leaderboard")
