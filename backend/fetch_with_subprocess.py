"""
Script to fetch Kaggle leaderboard using subprocess with --show flag
"""
import os
import subprocess
import pandas as pd
from io import StringIO

def fetch_leaderboard_subprocess(competition_slug):
    """
    Fetch leaderboard using Kaggle CLI via subprocess with --show flag
    """
    print(f"\n{'='*100}")
    print(f"FETCHING KAGGLE LEADERBOARD: {competition_slug.upper()}")
    print(f"{'='*100}\n")
    
    # Create temp directory
    download_dir = 'temp_leaderboard'
    os.makedirs(download_dir, exist_ok=True)
    
    # Get the path to kaggle executable in venv
    kaggle_exe = r"C:\GitHub\ML-Battle\backend\venv\Scripts\kaggle.exe"
    
    # Build the CLI command with --show --csv flags
    cmd = [
        kaggle_exe,
        'competitions',
        'leaderboard',
        competition_slug,
        '--show',
        '--csv'
    ]
    
    print(f"🔄 Running command: {' '.join(cmd)}\n")
    
    try:
        # Run the command using subprocess
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            print(f"❌ Command failed with return code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return None
        
        if result.stdout:
            print("✅ Command executed successfully!\n")
            
            # Save the CSV output
            csv_output_path = os.path.join(download_dir, f'{competition_slug}_leaderboard_subprocess.csv')
            with open(csv_output_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            print(f"💾 Raw CSV data saved to: {csv_output_path}\n")
            
            # Parse the CSV
            try:
                df = pd.read_csv(StringIO(result.stdout))
                
                print(f"{'='*100}")
                print(f"LEADERBOARD DATA - {len(df)} ENTRIES")
                print(f"{'='*100}\n")
                
                print(f"Columns: {', '.join(df.columns.tolist())}\n")
                
                # Display header
                print(f"{'='*100}")
                print(f"{'Rank':<8} {'Team Name':<50} {'Score':<15} {'Entries':<10}")
                print(f"{'='*100}")
                
                # Display all entries
                for idx, row in df.iterrows():
                    rank = idx + 1
                    
                    # Try different column name variations
                    team = str(row.get('teamName', row.get('TeamName', row.get('team', 'Unknown'))))
                    score = row.get('score', row.get('Score', row.get('publicScore', 'N/A')))
                    entries = row.get('submissionCount', row.get('SubmittedCount', row.get('entries', 'N/A')))
                    
                    # Truncate long team names
                    display_team = team[:48] + '..' if len(team) > 50 else team
                    
                    print(f"{rank:<8} {display_team:<50} {str(score):<15} {str(entries):<10}")
                
                print(f"{'='*100}\n")
                
                # Statistics
                print(f"{'='*100}")
                print("📊 STATISTICS:")
                print(f"{'='*100}")
                
                # Try to find the score column
                score_col = None
                for col in ['score', 'Score', 'publicScore', 'PublicScore']:
                    if col in df.columns:
                        score_col = col
                        break
                
                if score_col:
                    scores = pd.to_numeric(df[score_col], errors='coerce')
                    print(f"🏆 Top Score:        {scores.max():.6f}")
                    print(f"📊 Average Score:    {scores.mean():.6f}")
                    print(f"📈 Median Score:     {scores.median():.6f}")
                    print(f"📉 Lowest Score:     {scores.min():.6f}")
                    print(f"📏 Std Deviation:    {scores.std():.6f}")
                else:
                    print("⚠️  Could not find score column for statistics")
                
                print(f"{'='*100}\n")
                
                # Display TOP 10
                print(f"{'='*100}")
                print("🏆 TOP 10 TEAMS:")
                print(f"{'='*100}\n")
                
                top_10 = df.head(10)
                for idx, row in top_10.iterrows():
                    rank = idx + 1
                    team = str(row.get('teamName', row.get('TeamName', row.get('team', 'Unknown'))))
                    score = row.get('score', row.get('Score', row.get('publicScore', 'N/A')))
                    print(f"#{rank:<4} {team:<55} Score: {score}")
                
                print(f"\n{'='*100}\n")
                
                # Show raw DataFrame info
                print("📋 DataFrame Info:")
                print(df.info())
                print("\n")
                
                return df
                
            except Exception as e:
                print(f"❌ Error parsing CSV: {e}")
                print("\nRaw output:")
                print(result.stdout[:1000])  # Print first 1000 chars
                import traceback
                traceback.print_exc()
        else:
            print("❌ No output from command")
        
        if result.stderr:
            print("\nWarnings/Messages:")
            print(result.stderr)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return None


if __name__ == "__main__":
    competition = "spaceship-titanic"
    
    print("🚀 Starting Kaggle leaderboard fetch using subprocess...\n")
    
    df = fetch_leaderboard_subprocess(competition)
    
    if df is not None:
        print("✅ SUCCESS: Leaderboard fetched and displayed using subprocess!")
    else:
        print("❌ FAILED: Could not fetch leaderboard")
