"""
Verify leaderboard data after sync
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'
USERNAME = 'darkdevil'
PASSWORD = 'sneha2604'
COMPETITION_ID = 6

# Login
login_response = requests.post(f'{BASE_URL}/auth/login/', json={'username': USERNAME, 'password': PASSWORD})
access_token = login_response.json()['tokens']['access']
headers = {'Authorization': f'Bearer {access_token}'}

# Get leaderboard
leaderboard_response = requests.get(f'{BASE_URL}/leaderboard/?competition={COMPETITION_ID}', headers=headers)
leaderboard_data = leaderboard_response.json()
leaderboard = leaderboard_data.get('results', leaderboard_data) if isinstance(leaderboard_data, dict) else leaderboard_data

print(f"Leaderboard Entries: {len(leaderboard)}")
print("\nTop 5 Entries:")
print("-" * 80)
print(f"{'Rank':<6} {'Team Name':<30} {'Score':<12} {'User':<15}")
print("-" * 80)

for entry in leaderboard[:5]:
    rank = entry.get('rank', 'N/A')
    team_name = entry.get('display_name') or entry.get('kaggle_team_name', 'Unknown')
    score = entry.get('score') or entry.get('best_score', 0)
    user = 'Platform User' if entry.get('user') else 'Kaggle Only'
    print(f"{rank:<6} {team_name[:29]:<30} {score:<12.4f} {user:<15}")

print("-" * 80)
print(f"\nPlatform users: {sum(1 for e in leaderboard if e.get('user'))}")
print(f"Kaggle-only: {sum(1 for e in leaderboard if not e.get('user'))}")
