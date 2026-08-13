from rest_framework import serializers


class ProfileUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class ProfileStatsSerializer(serializers.Serializer):
    total_xp = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    daily_xp = serializers.IntegerField()
    daily_xp_goal = serializers.IntegerField()
    hearts = serializers.IntegerField()
    max_hearts = serializers.IntegerField()


class ProfileProgressSerializer(serializers.Serializer):
    skills_completed = serializers.IntegerField()
    lessons_completed = serializers.IntegerField()


class ProfileResponseSerializer(serializers.Serializer):
    user = ProfileUserSerializer()
    stats = ProfileStatsSerializer()
    progress = ProfileProgressSerializer()


class StatsResponseSerializer(serializers.Serializer):
    total_xp = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    hearts = serializers.IntegerField()
    max_hearts = serializers.IntegerField()
    daily_xp = serializers.IntegerField()
    daily_xp_goal = serializers.IntegerField()