from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import (
    ProfileResponseSerializer,
    StatsResponseSerializer,
)
from drf_spectacular.utils import extend_schema


class ProfileAPIView(APIView):
    """
    Return the authenticated learner profile summary.
    """
    @extend_schema(
    responses={200: ProfileResponseSerializer},
    )
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Authentication is required.",
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = request.user
        stats = user.stats

        profile = {
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "stats": {
                "total_xp": stats.total_xp,
                "current_streak": stats.current_streak,
                "longest_streak": stats.longest_streak,
                "daily_xp": stats.daily_xp,
                "daily_xp_goal": stats.daily_xp_goal,
                "hearts": stats.hearts,
                "max_hearts": stats.max_hearts,
            },
            "progress": {
                "skills_completed": user.skill_progress.filter(
                    status="completed"
                ).count(),
                "lessons_completed": user.lesson_attempts.filter(
                    status="completed"
                ).count(),
            },
        }

        serializer = ProfileResponseSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class StatsAPIView(APIView):
    """
    Return the authenticated learner's gamification statistics.
    """
    @extend_schema(
    responses={200: StatsResponseSerializer},
    )
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Authentication is required.",
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        stats = request.user.stats

        data = {
            "total_xp": stats.total_xp,
            "current_streak": stats.current_streak,
            "longest_streak": stats.longest_streak,
            "hearts": stats.hearts,
            "max_hearts": stats.max_hearts,
            "daily_xp": stats.daily_xp,
            "daily_xp_goal": stats.daily_xp_goal,
        }

        serializer = StatsResponseSerializer(data)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator


@method_decorator(ensure_csrf_cookie, name="dispatch")
class SessionAPIView(APIView):
    """
    Ensure the active user session is established for the demo learner.
    Returns the authenticated user status and sets sessionid + csrftoken cookies.
    """
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            demo_user = User.objects.filter(username="demo_user").first()
            if demo_user:
                login(request, demo_user)
                request.user = demo_user

        if request.user and request.user.is_authenticated:
            return Response(
                {
                    "authenticated": True,
                    "user": {
                        "id": request.user.id,
                        "username": request.user.username,
                        "first_name": request.user.first_name,
                        "last_name": request.user.last_name,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "authenticated": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Demo user not found.",
                },
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )