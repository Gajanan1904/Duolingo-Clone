from django.db import models

from apps.courses.models import Skill


class Lesson(models.Model):
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    xp_reward = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["skill", "order"],
                name="unique_lesson_order_per_skill",
            )
        ]

    def __str__(self):
        return f"{self.skill.title} - {self.title}"


class Exercise(models.Model):
    class ExerciseType(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
        TRANSLATE = "translate", "Translate"
        WORD_BANK = "word_bank", "Word Bank"
        MATCH_PAIRS = "match_pairs", "Match Pairs"
        FILL_BLANK = "fill_blank", "Fill in the Blank"
        TYPE_ANSWER = "type_answer", "Type Answer"

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="exercises",
    )
    type = models.CharField(
        max_length=30,
        choices=ExerciseType.choices,
    )
    question = models.TextField()
    data = models.JSONField(default=dict)
    correct_answer = models.JSONField(default=dict)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "order"],
                name="unique_exercise_order_per_lesson",
            )
        ]

    def __str__(self):
        return f"{self.lesson.title} - Exercise {self.order}"