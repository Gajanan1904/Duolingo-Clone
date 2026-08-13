from django.urls import path

from apps.gamification.views import (
    HeartRefillAPIView,
    LeaderboardAPIView,
)


urlpatterns = [
    path(
        "leaderboard/",
        LeaderboardAPIView.as_view(),
        name="leaderboard",
    ),
    path(
        "practice/hearts/",
        HeartRefillAPIView.as_view(),
        name="heart-refill",
    ),
]