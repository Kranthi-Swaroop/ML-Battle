"""
Final script to fetch Kaggle leaderboard using subprocess
"""
import os
import subprocess
import re
import pandas as pd

def fetch_leaderboard_with_subprocess(competition_slug):
    """
    Fetch leaderboard using Kaggle CLI via subprocess
    """
    print(f"\n{'='*100}")
    print(f"KAGGLE COMPETITION LEADERBOARD: {competition_slug.upper()}")
    print(f"{'='*100}\n")
    
    # Create temp directory
    download_dir = 'temp_leaderboard'
    os.makedirs(download_dir, exist_ok=True)
    
    # Get the path to kaggle executable in venv
    kaggle_exe = r"C:\GitHub\ML-Battle\backend\venv\Scripts\kaggle.exe"
    
    # Build the CLI command
    cmd = [
        kaggle_exe,
        'competitions',
        'leaderboard',
        competition_slug,
        '--show'
    ]
    
    print(f"🔄 Running command via subprocess.run():")
    print(f"   {' '.join(cmd)}\n")
    
    try:
        # Run the command using subprocess
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            errors='replace'  # Replace invalid Unicode characters
        )
        
        if result.stdout:
            print("✅ Command executed successfully!\n")
            print(f"{'='*100}")
            print("RAW OUTPUT FROM KAGGLE CLI:")
            print(f"{'='*100}\n")
            print(result.stdout)
            print(f"\n{'='*100}\n")
            
            # Parse the tabular output
            lines = result.stdout.strip().split('\n')
            
            # Find the data lines (skip warning and header)
            data_lines = []
            for line in lines:
                # Skip warning lines, header lines, and separator lines
                if ('Warning:' in line or 
                    'teamId' in line or 
                    '---' in line or 
                    'please consider' in line or
                    len(line.strip()) == 0):
                    continue
                data_lines.append(line)
            
            if data_lines:
                print(f"📊 Parsed {len(data_lines)} leaderboard entries\n")
                
                # Parse each line
                parsed_data = []
                for line in data_lines:
                    # Split by multiple spaces
                    parts = re.split(r'\s{2,}', line.strip())
                    
                    if len(parts) >= 4:
                        team_id = parts[0].strip()
                        team_name = parts[1].strip()
                        submission_date = parts[2].strip()
                        score = parts[3].strip()
                        
                        parsed_data.append({
                            'Rank': len(parsed_data) + 1,
                            'TeamId': team_id,
                            'TeamName': team_name,
                            'SubmissionDate': submission_date,
                            'Score': float(score)
                        })
                
                # Create DataFrame
                df = pd.DataFrame(parsed_data)
                
                # Save to CSV
                csv_path = os.path.join(download_dir, f'{competition_slug}_subprocess_leaderboard.csv')
                df.to_csv(csv_path, index=False, encoding='utf-8')
                
                print(f"{'='*100}")
                print(f"FORMATTED LEADERBOARD TABLE")
                print(f"{'='*100}\n")
                
                # Display formatted table
                print(f"{'Rank':<8} {'Team Name':<50} {'Score':<15} {'Date':<20}")
                print(f"{'='*100}")
                
                for _, row in df.iterrows():
                    rank = row['Rank']
                    team = row['TeamName']
                    score = row['Score']
                    date = row['SubmissionDate']
                    
                    # Truncate long names
                    display_team = team[:48] + '..' if len(team) > 50 else team
                    
                    print(f"{rank:<8} {display_team:<50} {score:<15.5f} {date:<20}")
                
                print(f"{'='*100}\n")
                
                # Statistics
                print(f"{'='*100}")
                print("📊 STATISTICS:")
                print(f"{'='*100}")
                
                scores = df['Score']
                print(f"🏆 Top Score:        {scores.max():.6f}")
                print(f"📊 Average Score:    {scores.mean():.6f}")
                print(f"📈 Median Score:     {scores.median():.6f}")
                print(f"📉 Lowest Score:     {scores.min():.6f}")
                print(f"📏 Std Deviation:    {scores.std():.6f}")
                print(f"📋 Total Entries:    {len(df)}")
                
                print(f"\n💾 Data saved to: {csv_path}")
                print(f"{'='*100}\n")
                
                # Display TOP 10
                print(f"{'='*100}")
                print("🏆 TOP 10 TEAMS:")
                print(f"{'='*100}\n")
                
                top_10 = df.head(10)
                for _, row in top_10.iterrows():
                    print(f"#{row['Rank']:<4} {row['TeamName']:<55} Score: {row['Score']:.5f}")
                
                print(f"\n{'='*100}\n")
                
                return df
            else:
                print("❌ No data lines found in output")
        else:
            print("❌ No output from command")
        
        if result.stderr:
            print("\n⚠️  Warnings/Messages:")
            print(result.stderr)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return None


if __name__ == "__main__":
    competition = "spaceship-titanic"
    
    print("🚀 Fetching Kaggle leaderboard using OS subprocess...\n")
    
    df = fetch_leaderboard_with_subprocess(competition)
    
    if df is not None:
        print("✅ SUCCESS: Leaderboard fetched, parsed, and displayed using subprocess!")
        print(f"   Method: subprocess.run() with kaggle CLI command")
        print(f"   Data captured from stdout and parsed into DataFrame")
    else:
        print("❌ FAILED: Could not fetch leaderboard")
