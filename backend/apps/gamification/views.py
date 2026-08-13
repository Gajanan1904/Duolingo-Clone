from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.gamification.leaderboard_service import LeaderboardService
from apps.gamification.services import GamificationService
from apps.gamification.serializers import (
    HeartRefillResponseSerializer,
    LeaderboardResponseSerializer,
)
from drf_spectacular.utils import extend_schema


class LeaderboardAPIView(APIView):
    """
    Return the XP leaderboard.
    """
    @extend_schema(
    responses={200: LeaderboardResponseSerializer},
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

        result = LeaderboardService.get_leaderboard(
            request.user
        )

        leaderboard = [
            {
                "rank": entry["rank"],
                "user": {
                    "id": entry["user_id"],
                    "username": entry["username"],
                },
                "xp": entry["total_xp"],
            }
            for entry in result
        ]

        current_user_rank = next(
            (
                entry["rank"]
                for entry in result
                if entry["is_current_user"]
            ),
            None,
        )

        if current_user_rank is None:
            current_user_rank = len(result) + 1

        response_data = {
            "leaderboard": leaderboard,
            "current_user_rank": current_user_rank,
        }

        serializer = LeaderboardResponseSerializer(
            response_data
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class HeartRefillAPIView(APIView):
    """
    Refill learner hearts up to max_hearts.
    """
    @extend_schema(
    request=None,
    responses={200: HeartRefillResponseSerializer},
    )
    def post(self, request):
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

        result = GamificationService.refill_hearts(
            request.user
        )

        response_data = {
            "success": True,
            "hearts": {
                "current": result.hearts,
                "max": result.max_hearts,
            },
        }

        serializer = HeartRefillResponseSerializer(
            response_data
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )