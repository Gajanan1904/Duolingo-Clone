from datetime import date, datetime, time, timedelta

from django.db import transaction
from django.utils import timezone

from apps.gamification.models import UserStats


class StreakService:
    """Business logic for learner streaks."""

    @staticmethod
    def _normalize_date(value):
        """Convert date/datetime into a calendar date."""

        if value is None:
            return timezone.localdate()

        if isinstance(value, datetime):
            if timezone.is_aware(value):
                value = timezone.localtime(value)

            return value.date()

        if isinstance(value, date):
            return value

        raise ValueError(
            "activity_date must be a date or datetime."
        )

    @staticmethod
    def _activity_datetime(activity_date):
        """Convert activity date into a timezone-aware datetime."""

        if isinstance(activity_date, datetime):
            if timezone.is_aware(activity_date):
                return activity_date

            return timezone.make_aware(
                activity_date,
                timezone.get_current_timezone(),
            )

        return timezone.make_aware(
            datetime.combine(
                activity_date,
                time.min,
            ),
            timezone.get_current_timezone(),
        )

    @staticmethod
    @transaction.atomic
    def update_streak(user, activity_date=None):
        """Update the learner's calendar-day streak."""

        activity_day = StreakService._normalize_date(
            activity_date
        )

        stats = (
            UserStats.objects
            .select_for_update()
            .get(user=user)
        )

        if stats.last_activity is None:
            stats.current_streak = 1

        else:
            last_activity_day = StreakService._normalize_date(
                stats.last_activity
            )

            if activity_day == last_activity_day:
                pass

            elif activity_day == (
                last_activity_day + timedelta(days=1)
            ):
                stats.current_streak += 1

            elif activity_day > (
                last_activity_day + timedelta(days=1)
            ):
                stats.current_streak = 1

            else:
                pass

        stats.longest_streak = max(
            stats.longest_streak,
            stats.current_streak,
        )

        stats.last_activity = (
            StreakService._activity_datetime(activity_day)
        )

        stats.save(
            update_fields=[
                "current_streak",
                "longest_streak",
                "last_activity",
                "updated_at",
            ]
        )

        return stats