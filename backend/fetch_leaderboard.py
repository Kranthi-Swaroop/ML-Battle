"""
Script to fetch and display Kaggle competition leaderboard
"""
import os
import zipfile
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi

def fetch_and_display_leaderboard(competition_slug):
    """
    Fetch leaderboard from Kaggle and display it
    """
    # Initialize Kaggle API
    api = KaggleApi()
    api.authenticate()
    
    print(f"Fetching leaderboard for: {competition_slug}")
    
    # Create temp directory for downloads
    download_dir = os.path.join(os.path.dirname(__file__), 'temp_leaderboard')
    os.makedirs(download_dir, exist_ok=True)
    
    # Try to download leaderboard using API method
    try:
        # Download the leaderboard
        leaderboard_file = os.path.join(download_dir, f'{competition_slug}.zip')
        
        # Use the competition_leaderboard_download method
        print("Downloading leaderboard...")
        api.competition_leaderboard_download(competition_slug, path=download_dir)
        
        # Find the downloaded zip file
        zip_files = [f for f in os.listdir(download_dir) if f.endswith('.zip')]
        
        if zip_files:
            zip_path = os.path.join(download_dir, zip_files[0])
            print(f"Found zip file: {zip_files[0]}")
            
            # Extract the zip file
            print("Extracting zip file...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
            
            # Find CSV files
            csv_files = [f for f in os.listdir(download_dir) if f.endswith('.csv')]
            
            if csv_files:
                csv_path = os.path.join(download_dir, csv_files[0])
                print(f"\nReading CSV file: {csv_files[0]}")
                
                # Read and display the leaderboard
                df = pd.read_csv(csv_path)
                
                print(f"\n{'='*80}")
                print(f"LEADERBOARD FOR: {competition_slug.upper()}")
                print(f"{'='*80}")
                print(f"\nTotal entries: {len(df)}")
                print(f"\nColumns: {', '.join(df.columns.tolist())}")
                
                print(f"\n{'='*80}")
                print("TOP 20 ENTRIES:")
                print(f"{'='*80}\n")
                
                # Display top 20
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                pd.set_option('display.max_colwidth', 30)
                
                print(df.head(20).to_string(index=False))
                
                print(f"\n{'='*80}")
                print(f"Full data saved at: {csv_path}")
                print(f"{'='*80}\n")
                
                return df
            else:
                print("No CSV files found in the extracted content")
        else:
            print("No zip files found after download")
            
    except Exception as e:
        print(f"Error downloading leaderboard: {e}")
        print("\nTrying alternative method using competition_leaderboard_view...")
        
        try:
            # Alternative: Get leaderboard view
            leaderboard = api.competition_leaderboard_view(competition_slug)
            
            print(f"\n{'='*80}")
            print(f"LEADERBOARD FOR: {competition_slug.upper()}")
            print(f"{'='*80}\n")
            
            # Display leaderboard entries
            if hasattr(leaderboard, 'submissions'):
                print(f"Total entries: {len(leaderboard.submissions)}\n")
                
                print(f"{'Rank':<6} {'Team':<30} {'Score':<12} {'Entries':<8}")
                print("-" * 80)
                
                for i, submission in enumerate(leaderboard.submissions[:20], 1):
                    team_name = submission.teamName[:28] if len(submission.teamName) > 28 else submission.teamName
                    print(f"{submission.rank:<6} {team_name:<30} {submission.score:<12} {submission.submittedCount:<8}")
                
                print(f"\n{'='*80}\n")
                
                # Convert to DataFrame
                data = []
                for submission in leaderboard.submissions:
                    data.append({
                        'TeamId': submission.teamId,
                        'TeamName': submission.teamName,
                        'SubmissionDate': submission.submissionDate,
                        'Score': submission.score,
                        'Rank': submission.rank,
                        'SubmittedCount': submission.submittedCount
                    })
                
                df = pd.DataFrame(data)
                
                # Save to CSV
                csv_path = os.path.join(download_dir, f'{competition_slug}_leaderboard.csv')
                df.to_csv(csv_path, index=False)
                print(f"Leaderboard saved to: {csv_path}\n")
                
                return df
            else:
                print("No submissions found in leaderboard")
                
        except Exception as e2:
            print(f"Alternative method also failed: {e2}")
    
    return None


if __name__ == "__main__":
    competition = "spaceship-titanic"
    df = fetch_and_display_leaderboard(competition)
    
    if df is not None:
        print("✅ Leaderboard fetched successfully!")
    else:
        print("❌ Failed to fetch leaderboard")
