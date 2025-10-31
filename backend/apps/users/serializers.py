from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    rating_tier = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'elo_rating', 'highest_rating',
            'competitions_participated', 'kaggle_username', 'bio',
            'avatar_url', 'rating_tier', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'elo_rating', 'highest_rating', 'competitions_participated',
            'created_at', 'updated_at'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'kaggle_username']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Detailed serializer for user profile."""
    rating_tier = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'elo_rating', 'highest_rating',
            'competitions_participated', 'kaggle_username', 'bio',
            'avatar_url', 'rating_tier', 'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'elo_rating', 'highest_rating', 'competitions_participated',
            'date_joined', 'created_at', 'updated_at'
        ]


class UserLeaderboardSerializer(serializers.ModelSerializer):
    """Lightweight serializer for leaderboard display."""
    rating_tier = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'elo_rating', 'rating_tier', 'competitions_participated']
