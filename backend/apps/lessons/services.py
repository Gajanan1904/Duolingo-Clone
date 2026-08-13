from django.db import transaction
from django.utils import timezone

from apps.lessons.models import Exercise, Lesson
from apps.lessons.exceptions import (
    ExerciseNotFoundError,
    InvalidAnswerError,
    InvalidAttemptError,
    InvalidExerciseError,
    LessonAlreadyCompletedError,
    LessonNotCompletedError,
    LessonNotFoundError,
    SkillLockedError,
)
from apps.progress.models import LessonAttempt
from apps.progress.services import ProgressService
from apps.gamification.models import UserStats
from apps.gamification.services import GamificationService
from apps.gamification.streak_service import StreakService
from apps.progress.models import LessonAttempt, SkillProgress


class LessonService:
    """Business logic for lesson execution."""

    VALID_EXERCISE_TYPES = {
        "multiple_choice",
        "translate",
        "word_bank",
        "match_pairs",
        "fill_blank",
        "type_answer",
    }

    @staticmethod
    def get_lesson(user, lesson_id):
        try:
            lesson = (
                Lesson.objects
                .select_related("skill__unit__course")
                .prefetch_related("exercises")
                .get(id=lesson_id)
            )
        except Lesson.DoesNotExist:
            raise LessonNotFoundError()

        skill_status = ProgressService.calculate_skill_status(
            user,
            lesson.skill,
        )

        if skill_status == ProgressService.SKILL_STATUS_LOCKED:
            raise SkillLockedError()

        lesson_exercises = []

        for exercise in lesson.exercises.all().order_by("order"):
            lesson_exercises.append(
                {
                    "id": exercise.id,
                    "type": exercise.type,
                    "question": exercise.question,
                    "data": exercise.data,
                    "order": exercise.order,
                }
            )

        return {
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "skill_id": lesson.skill_id,
            "xp_reward": lesson.xp_reward,
            "total_exercises": len(lesson_exercises),
            "exercises": lesson_exercises,
        }

    @staticmethod
    @transaction.atomic
    def start_lesson(user, lesson_id):
        try:
            lesson = (
                Lesson.objects
                .select_related("skill__unit__course")
                .get(id=lesson_id)
            )
        except Lesson.DoesNotExist:
            raise LessonNotFoundError()

        skill_status = ProgressService.calculate_skill_status(
            user,
            lesson.skill,
        )

        if skill_status == ProgressService.SKILL_STATUS_LOCKED:
            raise SkillLockedError()

        existing_attempt = (
            LessonAttempt.objects
            .filter(
                user=user,
                lesson=lesson,
                status="in_progress",
            )
            .order_by("-started_at")
            .first()
        )

        if existing_attempt:
            return existing_attempt

        return LessonAttempt.objects.create(
            user=user,
            lesson=lesson,
            correct_answers=0,
            total_questions=lesson.exercises.count(),
            xp_earned=0,
            hearts_lost=0,
            status="in_progress",
        )

    @staticmethod
    def _get_exercise(lesson, exercise_id):
        try:
            return lesson.exercises.get(id=exercise_id)
        except Exercise.DoesNotExist:
            raise ExerciseNotFoundError()

    @staticmethod
    def _validate_attempt(attempt):
        if attempt is None:
            raise InvalidAttemptError()

        if attempt.status != "in_progress":
            raise InvalidAttemptError()

    @staticmethod
    def _normalize_text(value):
        if not isinstance(value, str):
            raise InvalidAnswerError()

        return value.strip().casefold()

    @staticmethod
    def _validate_multiple_choice(exercise, answer):
        if not isinstance(answer, dict):
            raise InvalidAnswerError()

        value = answer.get("value")
        expected = exercise.correct_answer.get("value")

        if value is None or expected is None:
            raise InvalidAnswerError()

        return value == expected

    @staticmethod
    def _validate_text_answer(exercise, answer):
        if not isinstance(answer, dict):
            raise InvalidAnswerError()

        value = answer.get("value")
        expected = exercise.correct_answer.get("value")

        if value is None or expected is None:
            raise InvalidAnswerError()

        return (
            LessonService._normalize_text(value)
            == LessonService._normalize_text(expected)
        )

    @staticmethod
    def _validate_word_bank(exercise, answer):
        if not isinstance(answer, dict):
            raise InvalidAnswerError()

        submitted = answer.get("words")
        expected = exercise.correct_answer.get("words")

        if not isinstance(submitted, list):
            raise InvalidAnswerError()

        if not isinstance(expected, list):
            raise InvalidExerciseError()

        return submitted == expected

    @staticmethod
    def _validate_match_pairs(exercise, answer):
        if not isinstance(answer, dict):
            raise InvalidAnswerError()

        submitted = answer.get("pairs")
        expected = exercise.correct_answer.get("pairs")

        if not isinstance(submitted, dict):
            raise InvalidAnswerError()

        if not isinstance(expected, dict):
            raise InvalidExerciseError()

        return submitted == expected

    @staticmethod
    def _validate_answer(exercise, answer):
        if exercise.type not in LessonService.VALID_EXERCISE_TYPES:
            raise InvalidExerciseError()

        if not isinstance(exercise.correct_answer, dict):
            raise InvalidExerciseError()

        if exercise.type == "multiple_choice":
            return LessonService._validate_multiple_choice(
                exercise,
                answer,
            )

        if exercise.type in {
            "translate",
            "type_answer",
            "fill_blank",
        }:
            return LessonService._validate_text_answer(
                exercise,
                answer,
            )

        if exercise.type == "word_bank":
            return LessonService._validate_word_bank(
                exercise,
                answer,
            )

        if exercise.type == "match_pairs":
            return LessonService._validate_match_pairs(
                exercise,
                answer,
            )

        raise InvalidExerciseError()

    @staticmethod
    @transaction.atomic
    def submit_answer(user, lesson_id, exercise_id, answer):
        try:
            lesson = (
                Lesson.objects
                .select_related("skill__unit__course")
                .get(id=lesson_id)
            )
        except Lesson.DoesNotExist:
            raise LessonNotFoundError()

        attempt = (
            LessonAttempt.objects
            .select_for_update()
            .filter(
                user=user,
                lesson=lesson,
                status="in_progress",
            )
            .order_by("-started_at")
            .first()
        )

        LessonService._validate_attempt(attempt)

        exercise = LessonService._get_exercise(
            lesson,
            exercise_id,
        )

        is_correct = LessonService._validate_answer(
            exercise,
            answer,
        )

        stats = (
            UserStats.objects
            .select_for_update()
            .get(user=user)
        )

        if is_correct:
            attempt.correct_answers += 1
        else:
            if stats.hearts <= 0:
                attempt.status = "failed"
                attempt.save(update_fields=["status"])
                raise InvalidAttemptError(
                    "Lesson attempt has failed because hearts are exhausted."
                )

            GamificationService.deduct_heart(user)

            attempt.hearts_lost += 1

            stats.refresh_from_db()

            if stats.hearts <= 0:
                attempt.status = "failed"

        attempt.save()

        return {
            "correct": is_correct,
            "exercise_id": exercise.id,
            "hearts": {
                "current": stats.hearts,
                "max": stats.max_hearts,
            },
            "lesson": {
                "status": attempt.status,
            },
            "attempt": attempt,
        }

    @staticmethod
    @transaction.atomic
    def complete_lesson(user, lesson_id, attempt):
        """
        Complete a lesson exactly once and apply all rewards/progress.
        """

        try:
            lesson = (
                Lesson.objects
                .select_related("skill__unit__course")
                .get(id=lesson_id)
            )
        except Lesson.DoesNotExist:
            raise LessonNotFoundError()

        locked_attempt = (
            LessonAttempt.objects
            .select_for_update()
            .get(id=attempt.id)
        )

        if locked_attempt.user_id != user.id:
            raise InvalidAttemptError()

        if locked_attempt.lesson_id != lesson.id:
            raise InvalidAttemptError()

        if locked_attempt.status == "completed":
            raise LessonAlreadyCompletedError()

        if locked_attempt.status != "in_progress":
            raise InvalidAttemptError()

        if locked_attempt.correct_answers < locked_attempt.total_questions:
            raise LessonNotCompletedError()

        if locked_attempt.total_questions != lesson.exercises.count():
            raise LessonNotCompletedError()

        stats = (
            UserStats.objects
            .select_for_update()
            .get(user=user)
        )

        previous_activity = stats.last_activity
        today = timezone.localdate()

        # Update streak before XP so streak sees the previous activity date.
        StreakService.update_streak(
            user,
            activity_date=today,
        )

        # Reset daily XP if this is a new activity day.
        stats.refresh_from_db()

        if previous_activity and previous_activity.date() < today:
            stats.daily_xp = 0
            stats.save(
                update_fields=["daily_xp", "updated_at"]
            )

        # Award lesson XP exactly once.
        GamificationService.award_xp(
            user,
            lesson.xp_reward,
        )

        # One completed lesson = one crown, capped at lesson count.
        skill = lesson.skill

        skill_lessons_count = skill.lessons.count()

        completed_lessons = (
            LessonAttempt.objects
            .filter(
                user=user,
                lesson__skill=skill,
                status="completed",
            )
            .exclude(id=locked_attempt.id)
            .count()
        )

        completed_lessons += 1

        progress = int(
            (completed_lessons / skill_lessons_count) * 100
        )

        progress = max(0, min(100, progress))

        existing_progress = (
            SkillProgress.objects
            .select_for_update()
            .filter(
                user=user,
                skill=skill,
            )
        .first()
        )

        current_crowns = (
            existing_progress.crowns
            if existing_progress
            else 0
        )

        crowns = min(
            skill_lessons_count,
            current_crowns + 1,
        )

        skill_progress = ProgressService.update_skill_progress(
            user=user,
            skill=skill,
            progress=progress,
            crowns=crowns,
        )

        locked_attempt.xp_earned = lesson.xp_reward
        locked_attempt.status = "completed"
        locked_attempt.completed_at = timezone.now()
        locked_attempt.save()

        ProgressService.unlock_next_skill(
            user,
            skill,
        )

        stats.refresh_from_db()

        return {
            "success": True,
            "lesson": {
                "id": lesson.id,
                "status": locked_attempt.status,
            },
            "rewards": {
                "xp_earned": lesson.xp_reward,
            },
            "skill": {
                "id": skill.id,
                "progress": skill_progress.progress,
                "crowns": skill_progress.crowns,
                "status": skill_progress.status,
            },
            "stats": {
                "total_xp": stats.total_xp,
                "daily_xp": stats.daily_xp,
                "daily_xp_goal": stats.daily_xp_goal,
                "current_streak": stats.current_streak,
                "hearts": stats.hearts,
            },
        }

    @staticmethod
    @transaction.atomic
    def fail_lesson(user, attempt):
        """Mark an active lesson attempt as failed."""

        locked_attempt = (
            LessonAttempt.objects
            .select_for_update()
            .get(id=attempt.id)
        )

        if locked_attempt.user_id != user.id:
            raise InvalidAttemptError()

        if locked_attempt.status == "completed":
            raise LessonAlreadyCompletedError()

        if locked_attempt.status != "failed":
            locked_attempt.status = "failed"
            locked_attempt.completed_at = timezone.now()
            locked_attempt.save(
                update_fields=[
                    "status",
                    "completed_at",
                ]
            )

        return locked_attempt