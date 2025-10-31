"""
Deep dive into Kaggle API to find all available methods for leaderboard
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from kaggle.api.kaggle_api_extended import KaggleApi
import inspect

api = KaggleApi()
api.authenticate()

print(f"\n{'='*100}")
print("ANALYZING KAGGLE API LEADERBOARD METHODS")
print(f"{'='*100}\n")

# Get all leaderboard-related methods
leaderboard_methods = [m for m in dir(api) if 'leaderboard' in m.lower() and not m.startswith('_')]

print("Found leaderboard methods:")
for method in leaderboard_methods:
    func = getattr(api, method)
    print(f"\n{'-'*100}")
    print(f"Method: {method}")
    print(f"{'-'*100}")
    
    # Get function signature
    try:
        sig = inspect.signature(func)
        print(f"Signature: {method}{sig}")
        
        # Get docstring
        if func.__doc__:
            print(f"\nDocstring:")
            print(func.__doc__[:500])  # First 500 chars
    except Exception as e:
        print(f"Could not inspect: {e}")

print(f"\n{'='*100}")
print("TESTING competition_view_leaderboard METHOD")
print(f"{'='*100}\n")

# This might be different from competition_leaderboard_view
try:
    competition = "spaceship-titanic"
    
    # Try competition_view_leaderboard (note different order)
    result = api.competition_view_leaderboard(competition)
    
    print(f"Result type: {type(result)}")
    print(f"Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
    
    if hasattr(result, '__dict__'):
        print(f"Attributes: {result.__dict__}")
    
    if isinstance(result, list):
        print(f"\n✅ Got list with {len(result)} entries")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*100}")
print("CHECKING API SOURCE CODE LOCATION")
print(f"{'='*100}\n")

import kaggle
print(f"Kaggle package location: {kaggle.__file__}")
print(f"\nYou can check the source code at:")
print(f"C:\\GitHub\\ML-Battle\\backend\\venv\\Lib\\site-packages\\kaggle\\api\\kaggle_api_extended.py")

print(f"\n{'='*100}\n")
