from rest_framework import serializers


class LeaderboardUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user = LeaderboardUserSerializer()
    xp = serializers.IntegerField(min_value=0)


class LeaderboardResponseSerializer(serializers.Serializer):
    leaderboard = LeaderboardEntrySerializer(many=True)
    current_user_rank = serializers.IntegerField(min_value=1)


class HeartRefillHeartsSerializer(serializers.Serializer):
    current = serializers.IntegerField(min_value=0)
    max = serializers.IntegerField(min_value=0)


class HeartRefillResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    hearts = HeartRefillHeartsSerializer()