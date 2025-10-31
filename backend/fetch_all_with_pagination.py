"""
BREAKTHROUGH: Fetch ALL leaderboard entries using pagination!
The API returns 'nextPageToken' which means we can fetch more pages!
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd

api = KaggleApi()
api.authenticate()

def fetch_all_leaderboard_entries(competition_slug):
    """
    Fetch ALL leaderboard entries using pagination with nextPageToken
    """
    print(f"\n{'='*100}")
    print(f"🚀 FETCHING ALL LEADERBOARD ENTRIES WITH PAGINATION: {competition_slug.upper()}")
    print(f"{'='*100}\n")
    
    all_submissions = []
    page_token = None
    page_num = 1
    
    while True:
        print(f"📄 Fetching page {page_num}...")
        
        try:
            # Call the API method with page token
            if page_token:
                # The API might accept pageToken parameter
                result = api.competition_view_leaderboard(competition_slug, page_token=page_token)
            else:
                result = api.competition_view_leaderboard(competition_slug)
            
            if 'submissions' in result:
                submissions = result['submissions']
                print(f"   ✅ Got {len(submissions)} entries on page {page_num}")
                
                all_submissions.extend(submissions)
                
                # Check if there's a next page
                if 'nextPageToken' in result and result['nextPageToken']:
                    page_token = result['nextPageToken']
                    page_num += 1
                    print(f"   🔄 Next page token found, fetching more...\n")
                else:
                    print(f"   ✅ No more pages. Reached the end!\n")
                    break
            else:
                print(f"   ❌ No submissions found in result")
                break
                
        except TypeError as e:
            # If pageToken parameter is not supported, try alternative
            print(f"\n⚠️  pageToken parameter not supported: {e}")
            print(f"   The API method might not accept pagination parameters")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print(f"\n{'='*100}")
    print(f"📊 COMPLETE LEADERBOARD DATA")
    print(f"{'='*100}\n")
    
    print(f"✅ Total entries fetched: {len(all_submissions)}")
    
    if all_submissions:
        # Convert to DataFrame
        data = []
        for idx, sub in enumerate(all_submissions, 1):
            data.append({
                'Rank': idx,
                'TeamId': sub.get('teamId'),
                'TeamName': sub.get('teamName'),
                'Score': float(sub.get('score', 0)),
                'SubmissionDate': sub.get('submissionDate')
            })
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        csv_path = f'all_leaderboard_data/{competition_slug}_all_entries.csv'
        os.makedirs('all_leaderboard_data', exist_ok=True)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Display statistics
        print(f"\n{'='*100}")
        print("STATISTICS:")
        print(f"{'='*100}")
        print(f"🏆 Top Score:        {df['Score'].max():.6f}")
        print(f"📊 Average Score:    {df['Score'].mean():.6f}")
        print(f"📈 Median Score:     {df['Score'].median():.6f}")
        print(f"📉 Lowest Score:     {df['Score'].min():.6f}")
        print(f"📏 Std Deviation:    {df['Score'].std():.6f}")
        print(f"📋 Total Entries:    {len(df)}")
        
        print(f"\n💾 Complete data saved to: {csv_path}")
        
        # Display top 20
        print(f"\n{'='*100}")
        print("🏆 TOP 20 ENTRIES:")
        print(f"{'='*100}\n")
        
        print(f"{'Rank':<8} {'Team Name':<50} {'Score':<15}")
        print("="*100)
        
        for idx in range(min(20, len(df))):
            row = df.iloc[idx]
            display_team = row['TeamName'][:48] + '..' if len(row['TeamName']) > 50 else row['TeamName']
            print(f"{row['Rank']:<8} {display_team:<50} {row['Score']:<15.5f}")
        
        # Display last 20
        if len(df) > 40:
            print(f"\n{'='*100}")
            print(f"📋 LAST 20 ENTRIES (Ranks {len(df)-19} to {len(df)}):")
            print(f"{'='*100}\n")
            
            for idx in range(max(0, len(df)-20), len(df)):
                row = df.iloc[idx]
                display_team = row['TeamName'][:48] + '..' if len(row['TeamName']) > 50 else row['TeamName']
                print(f"{row['Rank']:<8} {display_team:<50} {row['Score']:<15.5f}")
        
        print(f"\n{'='*100}\n")
        
        return df
    else:
        print("❌ No entries fetched")
        return None


if __name__ == "__main__":
    competition = "spaceship-titanic"
    
    df = fetch_all_leaderboard_entries(competition)
    
    if df is not None:
        print(f"✅ SUCCESS: Fetched ALL {len(df)} entries for '{competition}'!")
    else:
        print(f"❌ FAILED")
