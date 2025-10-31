"""
Script to fetch Kaggle leaderboard using subprocess and CLI commands
"""
import os
import subprocess
import zipfile
import csv
import pandas as pd

def fetch_leaderboard_cli(competition_slug):
    """
    Fetch leaderboard using Kaggle CLI via subprocess
    """
    print(f"\n{'='*100}")
    print(f"FETCHING KAGGLE LEADERBOARD: {competition_slug.upper()}")
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
        '--download',
        '--path',
        download_dir
    ]
    
    print(f"Running command: {' '.join(cmd)}\n")
    
    try:
        # Run the command using subprocess
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        print("Command output:")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        
        # Check for downloaded files
        zip_files = [f for f in os.listdir(download_dir) if f.endswith('.zip')]
        
        if zip_files:
            zip_path = os.path.join(download_dir, zip_files[0])
            print(f"\n✅ Found zip file: {zip_files[0]}")
            
            # Extract the zip
            print(f"📦 Extracting zip file...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
            
            print(f"✅ Extraction complete!")
            
            # Find CSV files
            csv_files = [f for f in os.listdir(download_dir) if f.endswith('.csv')]
            
            if csv_files:
                csv_path = os.path.join(download_dir, csv_files[0])
                print(f"\n📄 Found CSV file: {csv_files[0]}")
                
                # Read and display the CSV
                df = pd.read_csv(csv_path)
                
                print(f"\n{'='*100}")
                print(f"LEADERBOARD DATA")
                print(f"{'='*100}\n")
                
                print(f"Total entries: {len(df)}")
                print(f"Columns: {', '.join(df.columns.tolist())}\n")
                
                # Display header
                print(f"{'='*100}")
                print(f"{'Rank':<8} {'Team Name':<50} {'Score':<15} {'Entries':<10}")
                print(f"{'='*100}")
                
                # Display all entries
                for idx, row in df.iterrows():
                    rank = idx + 1
                    team = str(row.get('TeamName', 'Unknown'))
                    score = row.get('Score', 'N/A')
                    entries = row.get('SubmittedCount', 'N/A')
                    
                    # Truncate long team names
                    display_team = team[:48] + '..' if len(team) > 50 else team
                    
                    print(f"{rank:<8} {display_team:<50} {str(score):<15} {str(entries):<10}")
                
                print(f"{'='*100}\n")
                
                # Statistics
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
                
                print(f"\n💾 Data saved at: {csv_path}")
                print(f"{'='*100}\n")
                
                # Display TOP 10
                print(f"{'='*100}")
                print("🏆 TOP 10 TEAMS:")
                print(f"{'='*100}\n")
                
                top_10 = df.head(10)
                for idx, row in top_10.iterrows():
                    rank = idx + 1
                    team = row.get('TeamName', 'Unknown')
                    score = row.get('Score', 'N/A')
                    print(f"#{rank:<4} {team:<55} Score: {score}")
                
                print(f"\n{'='*100}\n")
                
                return df
            else:
                print("❌ No CSV files found after extraction")
        else:
            print("❌ No zip files downloaded")
            print("\nTrying alternative approach: direct CSV download...")
            
            # Alternative: try to download CSV directly
            cmd_csv = [
                kaggle_exe,
                'competitions',
                'leaderboard',
                competition_slug,
                '-v',
                '--csv'
            ]
            
            print(f"Running: {' '.join(cmd_csv)}\n")
            
            result = subprocess.run(
                cmd_csv,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout:
                # Save the CSV output
                csv_output_path = os.path.join(download_dir, f'{competition_slug}_leaderboard.csv')
                with open(csv_output_path, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                
                print(f"✅ CSV data saved to: {csv_output_path}\n")
                
                # Try to parse and display
                try:
                    df = pd.read_csv(csv_output_path)
                    
                    print(f"{'='*100}")
                    print(f"LEADERBOARD DATA (from CSV output)")
                    print(f"{'='*100}\n")
                    
                    print(df.to_string())
                    
                    return df
                except Exception as e:
                    print(f"Error parsing CSV: {e}")
            
            if result.stderr:
                print("Error output:")
                print(result.stderr)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return None


if __name__ == "__main__":
    competition = "spaceship-titanic"
    
    print("🚀 Starting Kaggle leaderboard fetch using subprocess...\n")
    
    df = fetch_leaderboard_cli(competition)
    
    if df is not None:
        print("✅ SUCCESS: Leaderboard fetched and displayed using subprocess!")
    else:
        print("❌ FAILED: Could not fetch leaderboard")
