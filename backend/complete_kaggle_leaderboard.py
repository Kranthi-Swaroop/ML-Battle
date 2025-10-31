"""
Complete Kaggle Leaderboard Fetcher using subprocess
Fetches ALL entries (not just top 20) from any Kaggle competition!
"""
import os
import sys
import subprocess
import zipfile
import pandas as pd

def fetch_complete_leaderboard(competition_slug):
    """
    Fetch COMPLETE leaderboard (all entries) for any Kaggle competition using subprocess
    
    Args:
        competition_slug (str): The Kaggle competition slug
    
    Returns:
        pd.DataFrame: Complete leaderboard data
    """
    print(f"\n{'='*100}")
    print(f"🏆 FETCHING COMPLETE KAGGLE LEADERBOARD: {competition_slug.upper()}")
    print(f"{'='*100}\n")
    
    # Create temp directory
    download_dir = 'complete_leaderboard'
    os.makedirs(download_dir, exist_ok=True)
    
    # Get the path to kaggle executable in venv
    kaggle_exe = r"C:\GitHub\ML-Battle\backend\venv\Scripts\kaggle.exe"
    
    # Build the CLI command with --download flag to get ALL entries
    cmd = [
        kaggle_exe,
        'competitions',
        'leaderboard',
        competition_slug,
        '--download',
        '--path',
        download_dir
    ]
    
    print(f"🔄 Downloading complete leaderboard using subprocess...")
    print(f"   Command: kaggle competitions leaderboard {competition_slug} --download\n")
    
    try:
        # Run the command using subprocess
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            errors='replace'
        )
        
        print("📦 Download process completed!")
        
        if result.stdout:
            print(f"Output: {result.stdout}\n")
        
        # Look for downloaded zip file
        zip_files = [f for f in os.listdir(download_dir) if f.endswith('.zip')]
        
        if zip_files:
            zip_path = os.path.join(download_dir, zip_files[0])
            print(f"✅ Found zip file: {zip_files[0]}")
            print(f"📦 Extracting leaderboard data...\n")
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
            
            # Find CSV files
            csv_files = [f for f in os.listdir(download_dir) if f.endswith('.csv')]
            
            if csv_files:
                csv_path = os.path.join(download_dir, csv_files[0])
                print(f"✅ Found CSV file: {csv_files[0]}")
                
                # Read the CSV
                df = pd.read_csv(csv_path)
                
                print(f"\n{'='*100}")
                print(f"📊 COMPLETE LEADERBOARD DATA")
                print(f"{'='*100}\n")
                
                print(f"Total entries: {len(df)}")
                print(f"Columns: {', '.join(df.columns.tolist())}\n")
                
                # Add rank column if not present
                if 'Rank' not in df.columns:
                    df.insert(0, 'Rank', range(1, len(df) + 1))
                
                # Display first 20, middle 10, and last 10
                print(f"{'='*100}")
                print("📋 TOP 20 ENTRIES:")
                print(f"{'='*100}\n")
                
                print(f"{'Rank':<8} {'Team Name':<50} {'Score':<15}")
                print(f"{'='*100}")
                
                # Get the score column name (it might vary)
                score_col = None
                for col in ['Score', 'score', 'PublicScore', 'publicScore']:
                    if col in df.columns:
                        score_col = col
                        break
                
                team_col = None
                for col in ['TeamName', 'teamName', 'team', 'Team']:
                    if col in df.columns:
                        team_col = col
                        break
                
                if score_col and team_col:
                    # Show top 20
                    for idx in range(min(20, len(df))):
                        row = df.iloc[idx]
                        rank = idx + 1
                        team = str(row[team_col])
                        score = row[score_col]
                        
                        display_team = team[:48] + '..' if len(team) > 50 else team
                        print(f"{rank:<8} {display_team:<50} {str(score):<15}")
                    
                    print(f"{'='*100}\n")
                    
                    # Show middle entries if there are more than 50 entries
                    if len(df) > 50:
                        print(f"{'='*100}")
                        print(f"📋 MIDDLE 10 ENTRIES (around rank {len(df)//2}):")
                        print(f"{'='*100}\n")
                        
                        middle_start = (len(df) // 2) - 5
                        middle_end = middle_start + 10
                        
                        for idx in range(middle_start, min(middle_end, len(df))):
                            row = df.iloc[idx]
                            rank = idx + 1
                            team = str(row[team_col])
                            score = row[score_col]
                            
                            display_team = team[:48] + '..' if len(team) > 50 else team
                            print(f"{rank:<8} {display_team:<50} {str(score):<15}")
                        
                        print(f"{'='*100}\n")
                    
                    # Show last 10
                    if len(df) > 20:
                        print(f"{'='*100}")
                        print(f"📋 LAST 10 ENTRIES:")
                        print(f"{'='*100}\n")
                        
                        last_start = max(0, len(df) - 10)
                        
                        for idx in range(last_start, len(df)):
                            row = df.iloc[idx]
                            rank = idx + 1
                            team = str(row[team_col])
                            score = row[score_col]
                            
                            display_team = team[:48] + '..' if len(team) > 50 else team
                            print(f"{rank:<8} {display_team:<50} {str(score):<15}")
                        
                        print(f"{'='*100}\n")
                    
                    # Statistics
                    print(f"{'='*100}")
                    print("📊 STATISTICS:")
                    print(f"{'='*100}")
                    
                    scores = pd.to_numeric(df[score_col], errors='coerce')
                    print(f"🏆 Top Score:        {scores.max():.6f}")
                    print(f"📊 Average Score:    {scores.mean():.6f}")
                    print(f"📈 Median Score:     {scores.median():.6f}")
                    print(f"📉 Lowest Score:     {scores.min():.6f}")
                    print(f"📏 Std Deviation:    {scores.std():.6f}")
                    print(f"📋 Total Entries:    {len(df)}")
                    
                    # Save the complete data
                    output_csv = os.path.join(download_dir, f'{competition_slug}_complete_leaderboard.csv')
                    df.to_csv(output_csv, index=False, encoding='utf-8')
                    
                    print(f"\n💾 Complete leaderboard saved to: {output_csv}")
                    print(f"{'='*100}\n")
                    
                    # Show TOP 10
                    print(f"{'='*100}")
                    print("🏆 TOP 10 TEAMS:")
                    print(f"{'='*100}\n")
                    
                    top_10 = df.head(10)
                    for idx in range(len(top_10)):
                        row = top_10.iloc[idx]
                        rank = idx + 1
                        team = str(row[team_col])
                        score = row[score_col]
                        print(f"#{rank:<4} {team:<55} Score: {score}")
                    
                    print(f"\n{'='*100}\n")
                    
                else:
                    print("⚠️  Could not identify score or team columns")
                    print(f"Available columns: {df.columns.tolist()}")
                
                return df
            else:
                print("❌ No CSV files found after extraction")
        else:
            print("❌ No zip files downloaded")
            
            # Try alternative method: use --show with --csv to get some data
            print("\n⚠️  Download method failed. The --download flag might not work for this competition.")
            print("   This could mean:")
            print("   1. Competition doesn't allow full leaderboard download")
            print("   2. Only public leaderboard top entries are available")
            print("\n   Falling back to --show method (top 20 only)...\n")
            
            # Fall back to show method
            from universal_kaggle_leaderboard import fetch_any_competition_leaderboard
            return fetch_any_competition_leaderboard(competition_slug)
        
        if result.stderr and "Error" in result.stderr:
            print(f"\n⚠️  Stderr: {result.stderr}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return None


def main():
    """Main function"""
    
    if len(sys.argv) > 1:
        competition = sys.argv[1]
    else:
        print("🎯 Usage: python complete_kaggle_leaderboard.py <competition-slug>")
        print("\nExamples:")
        print("  python complete_kaggle_leaderboard.py titanic")
        print("  python complete_kaggle_leaderboard.py spaceship-titanic")
        print("\nEnter competition slug (or press Enter for 'spaceship-titanic'): ")
        
        competition = input().strip()
        if not competition:
            competition = "spaceship-titanic"
    
    print(f"\n🚀 Fetching COMPLETE leaderboard for: {competition}")
    print("   This will download ALL entries, not just top 20!\n")
    
    df = fetch_complete_leaderboard(competition)
    
    if df is not None:
        print(f"✅ SUCCESS: Complete leaderboard for '{competition}' fetched!")
        print(f"   Total entries: {len(df)}")
        print(f"   Method: subprocess with --download flag")
    else:
        print(f"❌ FAILED: Could not fetch complete leaderboard")


if __name__ == "__main__":
    main()
