from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.courses.models import Course, Skill, Unit
from apps.gamification.models import UserStats
from apps.gamification.services import GamificationService
from apps.gamification.streak_service import StreakService
from apps.lessons.exceptions import LessonAlreadyCompletedError
from apps.lessons.models import Exercise, Lesson
from apps.lessons.services import LessonService
from apps.progress.models import LessonAttempt, SkillProgress
from apps.gamification.leaderboard_service import LeaderboardService
from apps.lessons.exceptions import (
    InvalidAttemptError,
    LessonNotCompletedError,
)


class BusinessLogicTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test_user",
            password="test_password",
        )

        cls.course = Course.objects.create(
            name="Test Spanish",
            source_language="English",
            target_language="Spanish",
        )

        cls.unit = Unit.objects.create(
            course=cls.course,
            title="Unit 1",
            description="Test Unit",
            order=1,
        )

        cls.skill = Skill.objects.create(
            unit=cls.unit,
            title="Greetings",
            description="Basic greetings",
            order=1,
        )

        cls.lesson = Lesson.objects.create(
            skill=cls.skill,
            title="Basic Greetings",
            description="Test lesson",
            order=1,
            xp_reward=10,
        )

        UserStats.objects.create(
            user=cls.user,
            total_xp=0,
            current_streak=0,
            longest_streak=0,
            hearts=5,
            max_hearts=5,
            daily_xp_goal=20,
            daily_xp=0,
        )

    def setUp(self):
        self.stats = UserStats.objects.get(
            user=self.user
        )

    def _create_exercises(self):
        Exercise.objects.create(
            lesson=self.lesson,
            type="multiple_choice",
            question="What does Hola mean?",
            data={
                "options": [
                    "Hello",
                    "Goodbye",
                    "Thanks",
                ]
            },
            correct_answer={
                "value": "Hello"
            },
            order=1,
        )

        Exercise.objects.create(
            lesson=self.lesson,
            type="translate",
            question="Translate Hello",
            data={
                "source_text": "Hello"
            },
            correct_answer={
                "value": "Hola"
            },
            order=2,
        )

        Exercise.objects.create(
            lesson=self.lesson,
            type="word_bank",
            question="Build sentence",
            data={
                "words": [
                    "Yo",
                    "como",
                    "una",
                    "manzana",
                ]
            },
            correct_answer={
                "words": [
                    "Yo",
                    "como",
                    "una",
                    "manzana",
                ]
            },
            order=3,
        )

        Exercise.objects.create(
            lesson=self.lesson,
            type="match_pairs",
            question="Match words",
            data={},
            correct_answer={
                "pairs": {
                    "1": "Hola",
                    "2": "Adiós",
                }
            },
            order=4,
        )

        Exercise.objects.create(
            lesson=self.lesson,
            type="fill_blank",
            question="Yo ___ una manzana.",
            data={},
            correct_answer={
                "value": "como"
            },
            order=5,
        )

        Exercise.objects.create(
            lesson=self.lesson,
            type="type_answer",
            question="Translate Thank you",
            data={
                "source_text": "Thank you"
            },
            correct_answer={
                "value": "Gracias"
            },
            order=6,
        )

    def test_lesson_service_loads_lesson(self):
        lesson = LessonService.get_lesson(
            self.user,
            self.lesson.id,
        )

        self.assertEqual(
            lesson["id"],
            self.lesson.id,
        )

        self.assertEqual(
            lesson["total_exercises"],
            0,
        )

    def test_start_lesson_creates_attempt(self):
        attempt = LessonService.start_lesson(
            self.user,
            self.lesson.id,
        )

        self.assertEqual(
            attempt.status,
            "in_progress",
        )

        self.assertEqual(
            attempt.total_questions,
            0,
        )

        self.assertEqual(
            attempt.correct_answers,
            0,
        )

    def test_start_lesson_reuses_active_attempt(self):
        first = LessonService.start_lesson(
            self.user,
            self.lesson.id,
        )

        second = LessonService.start_lesson(
            self.user,
            self.lesson.id,
        )

        self.assertEqual(
            first.id,
            second.id,
        )

        self.assertEqual(
            LessonAttempt.objects.filter(
                user=self.user,
                lesson=self.lesson,
                status="in_progress",
            ).count(),
            1,
        )

    def test_all_six_exercise_types(self):
        self._create_exercises()

        attempt = LessonService.start_lesson(
            self.user,
            self.lesson.id,
        )

        answers = {
            1: {"value": "Hello"},
            2: {"value": "Hola"},
            3: {
                "words": [
                    "Yo",
                    "como",
                    "una",
                    "manzana",
                ]
            },
            4: {
                "pairs": {
                    "1": "Hola",
                    "2": "Adiós",
                }
            },
            5: {"value": "como"},
            6: {"value": "Gracias"},
        }

        for exercise_id, answer in answers.items():
            result = LessonService.submit_answer(
                self.user,
                self.lesson.id,
                exercise_id,
                answer,
            )

            self.assertTrue(
                result["correct"]
            )

        attempt.refresh_from_db()

        self.assertEqual(
            attempt.correct_answers,
            6,
        )

        self.assertEqual(
            attempt.hearts_lost,
            0,
        )

    def test_wrong_answer_deducts_one_heart(self):
        self._create_exercises()

        attempt = LessonService.start_lesson(
            self.user,
            self.lesson.id,
        )

        result = LessonService.submit_answer(
            self.user,
            self.lesson.id,
            1,
            {"value": "Goodbye"},
        )

        self.assertFalse(
            result["correct"]
        )

        self.stats.refresh_from_db()

        self.assertEqual(
            self.stats.hearts,
            4,
        )

        attempt.refresh_from_db()

        self.assertEqual(
            attempt.hearts_lost,
            1,
        )

    def test_out_of_hearts_fails_attempt(self):
        self._create_exercises()

        self.stats.hearts = 1
        self.stats.save()

        attempt = LessonService.start_lesson(
            self.user,
            self.lesson.id,
        )

        result = LessonService.submit_answer(
            self.user,
            self.lesson.id,
            1,
            {"value": "Wrong"},
        )

        self.assertFalse(
            result["correct"]
        )

        attempt.refresh_from_db()
        self.stats.refresh_from_db()

        self.assertEqual(
            self.stats.hearts,
            0,
        )

        self.assertEqual(
            attempt.status,
            "failed",
        )

    def test_heart_refill_never_exceeds_max(self):
        self.stats.hearts = 0
        self.stats.save()

        stats = GamificationService.refill_hearts(
            self.user
        )

        self.assertEqual(
            stats.hearts,
            stats.max_hearts,
        )

        stats = GamificationService.refill_hearts(
            self.user
        )

        self.assertEqual(
            stats.hearts,
            stats.max_hearts,
        )

    def test_lesson_completion_rewards(self):
        self._create_exercises()

        attempt = LessonService.start_lesson(
            self.user,
            self.lesson.id,
        )

        answers = {
            1: {"value": "Hello"},
            2: {"value": "Hola"},
            3: {
                "words": [
                    "Yo",
                    "como",
                    "una",
                    "manzana",
                ]
            },
            4: {
                "pairs": {
                    "1": "Hola",
                    "2": "Adiós",
                }
            },
            5: {"value": "como"},
            6: {"value": "Gracias"},
        }

        for exercise_id, answer in answers.items():
            LessonService.submit_answer(
                self.user,
                self.lesson.id,
                exercise_id,
                answer,
            )

        result = LessonService.complete_lesson(
            self.user,
            self.lesson.id,
            attempt,
        )

        attempt.refresh_from_db()
        self.stats.refresh_from_db()

        progress = SkillProgress.objects.get(
            user=self.user,
            skill=self.skill,
        )

        self.assertEqual(
            attempt.status,
            "completed",
        )

        self.assertEqual(
            attempt.xp_earned,
            10,
        )

        self.assertEqual(
            progress.progress,
            100,
        )

        self.assertEqual(
            progress.crowns,
            1,
        )

        self.assertEqual(
            progress.status,
            "completed",
        )

        self.assertEqual(
            self.stats.total_xp,
            10,
        )

        self.assertEqual(
            self.stats.daily_xp,
            10,
        )

        self.assertTrue(
            result["success"]
        )

    def test_lesson_completion_is_idempotent(self):
        self._create_exercises()

        attempt = LessonService.start_lesson(
            self.user,
            self.lesson.id,
        )

        attempt.correct_answers = 6
        attempt.total_questions = 6
        attempt.save()

        LessonService.complete_lesson(
            self.user,
            self.lesson.id,
            attempt,
        )

        self.stats.refresh_from_db()

        xp_before = self.stats.total_xp

        with self.assertRaises(
            LessonAlreadyCompletedError
        ):
            LessonService.complete_lesson(
                self.user,
                self.lesson.id,
                attempt,
            )

        self.stats.refresh_from_db()

        self.assertEqual(
            self.stats.total_xp,
            xp_before,
        )

    def test_same_day_streak_does_not_increase(self):
        stats = StreakService.update_streak(
            self.user
        )

        first_streak = stats.current_streak

        stats = StreakService.update_streak(
            self.user
        )

        self.assertEqual(
            stats.current_streak,
            first_streak,
        )

    def test_next_day_streak_increases(self):
        today = timezone.localdate()

        stats = StreakService.update_streak(
            self.user,
            today,
        )

        stats.last_activity = timezone.now() - timedelta(
            days=1
        )
        stats.save()

        stats = StreakService.update_streak(
            self.user,
            today,
        )

        self.assertEqual(
            stats.current_streak,
            2,
        )

    def test_missed_day_resets_streak(self):
        today = timezone.localdate()

        StreakService.update_streak(
            self.user,
            today,
        )

        self.stats.refresh_from_db()

        self.stats.last_activity = (
            timezone.now() - timedelta(days=3)
        )
        self.stats.save()

        stats = StreakService.update_streak(
            self.user,
            today,
        )

        self.assertEqual(
            stats.current_streak,
            1,
        )
        
    def test_leaderboard_orders_by_xp(self):
        second_user = User.objects.create_user(
            username="second_user",
            password="test_password",
        )

        third_user = User.objects.create_user(
            username="third_user",
            password="test_password",
        )

        UserStats.objects.create(
            user=second_user,
            total_xp=100,
            current_streak=2,
            longest_streak=2,
            hearts=5,
            max_hearts=5,
            daily_xp_goal=20,
            daily_xp=10,
        )

        UserStats.objects.create(
            user=third_user,
            total_xp=50,
            current_streak=1,
            longest_streak=1,
            hearts=5,
            max_hearts=5,
            daily_xp_goal=20,
            daily_xp=5,
        )

        self.stats.total_xp = 200
        self.stats.save()

        leaderboard = LeaderboardService.get_leaderboard(
            self.user
        )

        self.assertEqual(
            leaderboard[0]["username"],
            self.user.username,
        )

        self.assertEqual(
            leaderboard[1]["username"],
            second_user.username,
        )

        self.assertEqual(
            leaderboard[2]["username"],
            third_user.username,
        )

    def test_leaderboard_rank(self):
        second_user = User.objects.create_user(
            username="rank_user",
            password="test_password",
        )

        UserStats.objects.create(
            user=second_user,
            total_xp=500,
            current_streak=1,
            longest_streak=1,
            hearts=5,
            max_hearts=5,
            daily_xp_goal=20,
            daily_xp=0,
        )

        self.stats.total_xp = 100
        self.stats.save()

        leaderboard = LeaderboardService.get_leaderboard(
            self.user
        )

        current_user_entry = next(
            item
            for item in leaderboard
            if item["username"] == self.user.username
        )

        self.assertEqual(
            current_user_entry["rank"],
            2,
        )
        
    def test_failed_attempt_cannot_accept_more_answers(self):
        self._create_exercises()

        self.stats.hearts = 0
        self.stats.save()

        attempt = LessonService.start_lesson(
            self.user,
            self.lesson.id,
        )

        attempt.status = "failed"
        attempt.save()

        with self.assertRaises(
            InvalidAttemptError
        ):
            LessonService.submit_answer(
                self.user,
                self.lesson.id,
                1,
                {"value": "Hello"},
            )

    def test_completion_requires_all_questions_answered(self):
        self._create_exercises()

        attempt = LessonService.start_lesson(
            self.user,
            self.lesson.id,
        )

        with self.assertRaises(
            LessonNotCompletedError
        ):
            LessonService.complete_lesson(
                self.user,
                self.lesson.id,
                attempt,
            )

        attempt.refresh_from_db()

        self.assertEqual(
            attempt.status,
            "in_progress",
        )