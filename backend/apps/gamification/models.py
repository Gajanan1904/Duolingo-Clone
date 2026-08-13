from django.conf import settings
from django.db import models


class UserStats(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stats",
    )
    total_xp = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    hearts = models.PositiveIntegerField(default=5)
    max_hearts = models.PositiveIntegerField(default=5)
    daily_xp_goal = models.PositiveIntegerField(default=20)
    daily_xp = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Stats"