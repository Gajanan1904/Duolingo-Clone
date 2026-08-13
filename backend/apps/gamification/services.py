from datetime import datetime

from django.db import transaction
from django.utils import timezone

from apps.gamification.models import UserStats


class GamificationService:
    """Business logic for XP, hearts, daily XP, and heart refill."""

    @staticmethod
    def _activity_date(value):
        """Convert stored datetime/date values into a calendar date."""

        if value is None:
            return None

        if isinstance(value, datetime):
            if timezone.is_aware(value):
                value = timezone.localtime(value)

            return value.date()

        return value

    @staticmethod
    @transaction.atomic
    def award_xp(user, xp_amount):
        """Award XP and update daily XP atomically."""

        if xp_amount < 0:
            raise ValueError("XP amount cannot be negative.")

        stats, _ = (
            UserStats.objects
            .select_for_update()
            .get_or_create(
                user=user,
                defaults={
                    "total_xp": 0,
                    "current_streak": 0,
                    "longest_streak": 0,
                    "hearts": 5,
                    "max_hearts": 5,
                    "daily_xp_goal": 20,
                    "daily_xp": 0,
                },
            )
        )

        today = timezone.localdate()
        last_activity = GamificationService._activity_date(
            stats.last_activity
        )

        if last_activity and last_activity < today:
            stats.daily_xp = 0

        stats.total_xp += xp_amount
        stats.daily_xp += xp_amount
        stats.last_activity = timezone.now()

        stats.save()

        return stats

    @staticmethod
    @transaction.atomic
    def deduct_heart(user):
        """Deduct exactly one heart without going below zero."""

        stats = (
            UserStats.objects
            .select_for_update()
            .get(user=user)
        )

        if stats.hearts > 0:
            stats.hearts -= 1

        stats.save(
            update_fields=[
                "hearts",
                "updated_at",
            ]
        )

        return stats

    @staticmethod
    @transaction.atomic
    def update_daily_goal(user, xp_amount):
        """Update daily XP."""

        if xp_amount < 0:
            raise ValueError("XP amount cannot be negative.")

        stats = (
            UserStats.objects
            .select_for_update()
            .get(user=user)
        )

        today = timezone.localdate()
        last_activity = GamificationService._activity_date(
            stats.last_activity
        )

        if last_activity and last_activity < today:
            stats.daily_xp = 0

        stats.daily_xp += xp_amount
        stats.last_activity = timezone.now()

        stats.save(
            update_fields=[
                "daily_xp",
                "last_activity",
                "updated_at",
            ]
        )

        return stats

    @staticmethod
    @transaction.atomic
    def refill_hearts(user):
        """Restore hearts to max_hearts."""

        stats = (
            UserStats.objects
            .select_for_update()
            .get(user=user)
        )

        stats.hearts = stats.max_hearts

        stats.save(
            update_fields=[
                "hearts",
                "updated_at",
            ]
        )

        return stats