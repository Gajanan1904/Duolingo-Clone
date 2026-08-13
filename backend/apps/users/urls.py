from django.urls import path

from apps.users.views import ProfileAPIView, StatsAPIView, SessionAPIView


urlpatterns = [
    path(
        "auth/session/",
        SessionAPIView.as_view(),
        name="auth-session",
    ),
    path(
        "profile/",
        ProfileAPIView.as_view(),
        name="profile",
    ),
    path(
        "stats/",
        StatsAPIView.as_view(),
        name="stats",
    ),
]