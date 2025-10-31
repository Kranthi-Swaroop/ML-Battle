"""
Script to create sample competitions in the database
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.competitions.models import Competition
from django.contrib.auth import get_user_model

User = get_user_model()

def create_sample_competitions():
    print("Creating sample competitions...")
    print("-" * 50)
    
    # Create admin user if doesn't exist
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@mlbattle.com',
            password='admin123'
        )
        print("✅ Created admin user (username: admin, password: admin123)")
    else:
        print("ℹ️  Admin user already exists")
    
    # Sample competitions data
    competitions_data = [
        {
            'title': 'Titanic - Machine Learning from Disaster',
            'description': 'Use machine learning to create a model that predicts which passengers survived the Titanic shipwreck. This is the legendary Titanic ML competition – the best, first challenge for you to dive into ML competitions and familiarize yourself with how the Kaggle platform works.',
            'kaggle_competition_id': 'titanic',
            'kaggle_url': 'https://www.kaggle.com/c/titanic',
            'start_date': datetime.now() - timedelta(days=30),
            'end_date': datetime.now() + timedelta(days=60),
            'status': 'ongoing',
            'rating_weight': 1.0,
            'max_submissions_per_day': 5,
            'evaluation_metric': 'Accuracy',
            'prize_pool': 'Knowledge',
            'participants_count': 0
        },
        {
            'title': 'House Prices - Advanced Regression Techniques',
            'description': 'Ask a home buyer to describe their dream house, and they probably won\'t begin with the height of the basement ceiling or the proximity to an east-west railroad. But this playground competition\'s dataset proves that much more influences price negotiations than the number of bedrooms or a white-picket fence.',
            'kaggle_competition_id': 'house-prices-advanced-regression-techniques',
            'kaggle_url': 'https://www.kaggle.com/c/house-prices-advanced-regression-techniques',
            'start_date': datetime.now() - timedelta(days=20),
            'end_date': datetime.now() + timedelta(days=70),
            'status': 'ongoing',
            'rating_weight': 1.2,
            'max_submissions_per_day': 5,
            'evaluation_metric': 'RMSE',
            'prize_pool': '$15,000',
            'participants_count': 0
        },
        {
            'title': 'Digit Recognizer',
            'description': 'Learn computer vision fundamentals with the famous MNIST data. The goal in this competition is to take an image of a handwritten single digit, and determine what that digit is.',
            'kaggle_competition_id': 'digit-recognizer',
            'kaggle_url': 'https://www.kaggle.com/c/digit-recognizer',
            'start_date': datetime.now() - timedelta(days=15),
            'end_date': datetime.now() + timedelta(days=45),
            'status': 'ongoing',
            'rating_weight': 1.0,
            'max_submissions_per_day': 5,
            'evaluation_metric': 'Categorization Accuracy',
            'prize_pool': 'Knowledge',
            'participants_count': 0
        },
        {
            'title': 'Natural Language Processing with Disaster Tweets',
            'description': 'Predict which Tweets are about real disasters and which ones are not. Twitter has become an important communication channel in times of emergency. The ubiquitousness of smartphones enables people to announce an emergency they\'re observing in real-time.',
            'kaggle_competition_id': 'nlp-getting-started',
            'kaggle_url': 'https://www.kaggle.com/c/nlp-getting-started',
            'start_date': datetime.now() - timedelta(days=10),
            'end_date': datetime.now() + timedelta(days=80),
            'status': 'ongoing',
            'rating_weight': 1.1,
            'max_submissions_per_day': 5,
            'evaluation_metric': 'F1 Score',
            'prize_pool': '$10,000',
            'participants_count': 0
        },
        {
            'title': 'Store Sales - Time Series Forecasting',
            'description': 'Use machine learning to predict grocery sales. In this "Getting Started" competition, you\'ll use time-series forecasting to forecast store sales on data from Corporación Favorita, a large Ecuadorian-based grocery retailer.',
            'kaggle_competition_id': 'store-sales-time-series-forecasting',
            'kaggle_url': 'https://www.kaggle.com/c/store-sales-time-series-forecasting',
            'start_date': datetime.now() - timedelta(days=5),
            'end_date': datetime.now() + timedelta(days=55),
            'status': 'ongoing',
            'rating_weight': 1.3,
            'max_submissions_per_day': 5,
            'evaluation_metric': 'RMSLE',
            'prize_pool': 'Knowledge',
            'participants_count': 0
        },
        {
            'title': 'Spaceship Titanic',
            'description': 'Predict which passengers are transported to an alternate dimension. Welcome to the year 2912, where your data science skills are needed to solve a cosmic mystery. We\'ve received a transmission from four lightyears away and things aren\'t looking good.',
            'kaggle_competition_id': 'spaceship-titanic',
            'kaggle_url': 'https://www.kaggle.com/competitions/spaceship-titanic',
            'start_date': datetime.now() + timedelta(days=5),
            'end_date': datetime.now() + timedelta(days=95),
            'status': 'upcoming',
            'rating_weight': 1.0,
            'max_submissions_per_day': 5,
            'evaluation_metric': 'Classification Accuracy',
            'prize_pool': 'Knowledge',
            'participants_count': 0
        },
        {
            'title': 'Image Classification Challenge - Past Competition',
            'description': 'This was a popular image classification competition that has now ended. Check out the leaderboard and learn from the winning solutions!',
            'kaggle_competition_id': 'image-classification-past',
            'kaggle_url': 'https://www.kaggle.com/c/image-classification',
            'start_date': datetime.now() - timedelta(days=120),
            'end_date': datetime.now() - timedelta(days=30),
            'status': 'completed',
            'rating_weight': 1.5,
            'max_submissions_per_day': 5,
            'evaluation_metric': 'Log Loss',
            'prize_pool': '$50,000',
            'participants_count': 0
        },
    ]
    
    created_count = 0
    for comp_data in competitions_data:
        competition, created = Competition.objects.get_or_create(
            kaggle_competition_id=comp_data['kaggle_competition_id'],
            defaults=comp_data
        )
        
        if created:
            print(f"✅ Created: {competition.title}")
            created_count += 1
        else:
            print(f"ℹ️  Already exists: {competition.title}")
    
    print("-" * 50)
    print(f"✅ Created {created_count} new competitions")
    print(f"📊 Total competitions in database: {Competition.objects.count()}")
    print("\n🌐 Access Django Admin at: http://127.0.0.1:8000/admin/")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🔄 Refresh your competitions page to see them!")

if __name__ == "__main__":
    create_sample_competitions()
