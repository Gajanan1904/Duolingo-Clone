from django.contrib.auth.models import User

from apps.gamification.models import UserStats


class LeaderboardService:
    """Business logic for XP leaderboard."""

    @staticmethod
    def get_leaderboard(user=None, limit=10):
        """
        Return users ordered by total XP.

        The requesting user is included when possible.
        """

        users = (
            User.objects
            .select_related("stats")
            .filter(
                is_active=True,
                stats__isnull=False,
            )
            .order_by(
                "-stats__total_xp",
                "id",
            )[:limit]
        )

        leaderboard = []

        for rank, leaderboard_user in enumerate(
            users,
            start=1,
        ):
            stats = leaderboard_user.stats

            leaderboard.append(
                {
                    "rank": rank,
                    "user_id": leaderboard_user.id,
                    "username": leaderboard_user.username,
                    "total_xp": stats.total_xp,
                    "current_streak": stats.current_streak,
                    "is_current_user": (
                        user is not None
                        and leaderboard_user.id == user.id
                    ),
                }
            )

        return leaderboard