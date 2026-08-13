from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.lessons.models import Lesson
from apps.progress.models import LessonAttempt


class LessonAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_data")

        cls.user = User.objects.get(
            username="demo_user"
        )

        cls.lesson = Lesson.objects.get(id=1)

        cls.completable_lesson = Lesson.objects.get(id=2)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            user=self.user
        )

    # ============================================================
    # PATH API
    # ============================================================

    def test_learning_path(self):
        response = self.client.get(
            "/api/path/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        self.assertIn("course", body)
        self.assertIn("units", body)

        self.assertEqual(
            body["course"]["name"],
            "Spanish",
        )

        self.assertEqual(
            len(body["units"]),
            3,
        )

    def test_learning_path_unauthorized(self):
        client = APIClient()

        response = client.get(
            "/api/path/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "UNAUTHORIZED",
        )

    # ============================================================
    # LESSON RETRIEVAL
    # ============================================================

    def test_lesson_detail(self):
        response = self.client.get(
            f"/api/lessons/{self.lesson.id}/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        self.assertEqual(
            body["id"],
            self.lesson.id,
        )

        self.assertIn("title", body)
        self.assertIn("skill_id", body)
        self.assertIn("xp_reward", body)
        self.assertIn("total_exercises", body)
        self.assertIn("exercises", body)

        self.assertEqual(
            len(body["exercises"]),
            6,
        )

    def test_lesson_detail_does_not_expose_correct_answer(self):
        response = self.client.get(
            f"/api/lessons/{self.lesson.id}/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        # Mandatory security requirement.
        self.assertNotIn(
            "correct_answer",
            str(body),
        )

        for exercise in body["exercises"]:
            self.assertNotIn(
                "correct_answer",
                exercise,
            )

    def test_lesson_not_found(self):
        response = self.client.get(
            "/api/lessons/999999/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "LESSON_NOT_FOUND",
        )

    def test_lesson_unauthorized(self):
        client = APIClient()

        response = client.get(
            f"/api/lessons/{self.lesson.id}/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "UNAUTHORIZED",
        )

    # ============================================================
    # ANSWER API
    # ============================================================

    def test_submit_correct_answer(self):
        exercise = self.lesson.exercises.order_by(
            "order"
        ).first()

        response = self.client.post(
            f"/api/lessons/{self.lesson.id}/answer/",
            {
                "exercise_id": exercise.id,
                "answer": exercise.correct_answer,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        self.assertTrue(
            body["correct"]
        )

        self.assertEqual(
            body["exercise_id"],
            exercise.id,
        )

        self.assertIn(
            "feedback",
            body,
        )

        self.assertIn(
            "hearts",
            body,
        )

    def test_submit_wrong_answer_deducts_heart(self):
        exercise = self.lesson.exercises.order_by(
            "order"
        ).first()

        before = self.user.stats.hearts

        response = self.client.post(
            f"/api/lessons/{self.lesson.id}/answer/",
            {
                "exercise_id": exercise.id,
                "answer": {
                    "value": "__definitely_wrong__"
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        self.assertFalse(
            body["correct"]
        )

        self.assertEqual(
            body["hearts"]["current"],
            before - 1,
        )

        self.assertEqual(
            body["hearts"]["max"],
            self.user.stats.max_hearts,
        )

    def test_all_six_exercise_types(self):
        exercises = self.lesson.exercises.order_by(
            "order"
        )

        expected_types = {
            "multiple_choice",
            "translate",
            "word_bank",
            "match_pairs",
            "fill_blank",
            "type_answer",
        }

        actual_types = {
            exercise.type
            for exercise in exercises
        }

        self.assertEqual(
            actual_types,
            expected_types,
        )

        self.assertEqual(
            exercises.count(),
            6,
        )

        for exercise in exercises:
            response = self.client.post(
                f"/api/lessons/{self.lesson.id}/answer/",
                {
                    "exercise_id": exercise.id,
                    "answer": exercise.correct_answer,
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                200,
                msg=(
                    f"Failed for exercise type: "
                    f"{exercise.type}"
                ),
            )

            self.assertTrue(
                response.json()["correct"],
                msg=(
                    f"Incorrect result for exercise type: "
                    f"{exercise.type}"
                ),
            )

    def test_invalid_answer_request(self):
        response = self.client.post(
            f"/api/lessons/{self.lesson.id}/answer/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "INVALID_REQUEST",
        )

    def test_answer_unauthorized(self):
        client = APIClient()

        exercise = self.lesson.exercises.order_by(
            "order"
        ).first()

        response = client.post(
            f"/api/lessons/{self.lesson.id}/answer/",
            {
                "exercise_id": exercise.id,
                "answer": exercise.correct_answer,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "UNAUTHORIZED",
        )

    def test_out_of_hearts(self):
        self.user.stats.hearts = 0
        self.user.stats.save(
            update_fields=["hearts"]
        )

        exercise = self.lesson.exercises.order_by(
            "order"
        ).first()

        response = self.client.post(
            f"/api/lessons/{self.lesson.id}/answer/",
            {
                "exercise_id": exercise.id,
                "answer": {
                    "value": "__wrong__"
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        # Chat 3's existing domain behavior marks the
        # lesson attempt as failed when hearts are exhausted.
        self.assertEqual(
            response.json()["error"]["code"],
            "INVALID_ATTEMPT",
        )

        self.assertIn(
            "hearts are exhausted",
            response.json()["error"]["message"],
        )

    # ============================================================
    # COMPLETION API
    # ============================================================

    def test_complete_incomplete_lesson_rejected(self):
        exercise = self.completable_lesson.exercises.order_by(
            "order"
        ).first()

        response = self.client.post(
            f"/api/lessons/{self.completable_lesson.id}/answer/",
            {
                "exercise_id": exercise.id,
                "answer": {
                    "value": "__wrong__"
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        attempt = LessonAttempt.objects.filter(
            user=self.user,
            lesson=self.completable_lesson,
            status="in_progress",
        ).order_by("-id").first()

        self.assertIsNotNone(
            attempt
        )

        response = self.client.post(
            f"/api/lessons/{self.completable_lesson.id}/complete/",
            {
                "attempt_id": attempt.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "LESSON_NOT_COMPLETED",
        )

    def test_successful_lesson_completion(self):
        exercises = self.completable_lesson.exercises.order_by(
            "order"
        )

        before_xp = self.user.stats.total_xp

        for exercise in exercises:
            response = self.client.post(
                f"/api/lessons/{self.completable_lesson.id}/answer/",
                {
                    "exercise_id": exercise.id,
                    "answer": exercise.correct_answer,
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                200,
                msg=(
                    f"Answer failed for "
                    f"{exercise.type}"
                ),
            )

            self.assertTrue(
                response.json()["correct"]
            )

        attempt = LessonAttempt.objects.filter(
            user=self.user,
            lesson=self.completable_lesson,
            status="in_progress",
        ).order_by("-id").first()

        self.assertIsNotNone(
            attempt
        )

        response = self.client.post(
            f"/api/lessons/{self.completable_lesson.id}/complete/",
            {
                "attempt_id": attempt.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        self.assertTrue(
            body["success"]
        )

        self.assertEqual(
            body["lesson"]["id"],
            self.completable_lesson.id,
        )

        self.assertEqual(
            body["lesson"]["status"],
            "completed",
        )

        self.assertIn(
            "rewards",
            body,
        )

        self.assertIn(
            "xp_earned",
            body["rewards"],
        )

        self.assertIn(
            "skill",
            body,
        )

        self.assertIn(
            "progress",
            body["skill"],
        )

        self.assertIn(
            "crowns",
            body["skill"],
        )

        self.assertIn(
            "status",
            body["skill"],
        )

        self.assertIn(
            "stats",
            body,
        )

        self.user.refresh_from_db()

        self.assertGreaterEqual(
            self.user.stats.total_xp,
            before_xp,
        )

    def test_completion_is_idempotent(self):
        exercises = self.completable_lesson.exercises.order_by(
            "order"
        )

        for exercise in exercises:
            response = self.client.post(
                f"/api/lessons/{self.completable_lesson.id}/answer/",
                {
                    "exercise_id": exercise.id,
                    "answer": exercise.correct_answer,
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                200,
            )

        attempt = LessonAttempt.objects.filter(
            user=self.user,
            lesson=self.completable_lesson,
            status="in_progress",
        ).order_by("-id").first()

        self.assertIsNotNone(
            attempt
        )

        first_response = self.client.post(
            f"/api/lessons/{self.completable_lesson.id}/complete/",
            {
                "attempt_id": attempt.id,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            200,
        )

        self.user.refresh_from_db()

        xp_after_first = self.user.stats.total_xp

        second_response = self.client.post(
            f"/api/lessons/{self.completable_lesson.id}/complete/",
            {
                "attempt_id": attempt.id,
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            400,
        )

        self.assertEqual(
            second_response.json()["error"]["code"],
            "LESSON_ALREADY_COMPLETED",
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.stats.total_xp,
            xp_after_first,
        )

    def test_completion_unauthorized(self):
        client = APIClient()

        response = client.post(
            f"/api/lessons/{self.completable_lesson.id}/complete/",
            {
                "attempt_id": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "UNAUTHORIZED",
        )

    # ============================================================
    # PROFILE API
    # ============================================================

    def test_profile(self):
        response = self.client.get(
            "/api/profile/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        self.assertIn(
            "user",
            body,
        )

        self.assertIn(
            "stats",
            body,
        )

        self.assertIn(
            "progress",
            body,
        )

        self.assertEqual(
            body["user"]["username"],
            "demo_user",
        )

        self.assertIn(
            "total_xp",
            body["stats"],
        )

        self.assertIn(
            "current_streak",
            body["stats"],
        )

        self.assertIn(
            "hearts",
            body["stats"],
        )

        self.assertIn(
            "skills_completed",
            body["progress"],
        )

        self.assertIn(
            "lessons_completed",
            body["progress"],
        )

    def test_profile_unauthorized(self):
        client = APIClient()

        response = client.get(
            "/api/profile/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "UNAUTHORIZED",
        )

    # ============================================================
    # STATS API
    # ============================================================

    def test_stats(self):
        response = self.client.get(
            "/api/stats/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        expected_fields = {
            "total_xp",
            "current_streak",
            "longest_streak",
            "hearts",
            "max_hearts",
            "daily_xp",
            "daily_xp_goal",
        }

        self.assertTrue(
            expected_fields.issubset(
                body.keys()
            )
        )

    def test_stats_unauthorized(self):
        client = APIClient()

        response = client.get(
            "/api/stats/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "UNAUTHORIZED",
        )

    # ============================================================
    # LEADERBOARD API
    # ============================================================

    def test_leaderboard(self):
        response = self.client.get(
            "/api/leaderboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        self.assertIn(
            "leaderboard",
            body,
        )

        self.assertIn(
            "current_user_rank",
            body,
        )

        self.assertGreaterEqual(
            len(body["leaderboard"]),
            1,
        )

        first_entry = body["leaderboard"][0]

        self.assertIn(
            "rank",
            first_entry,
        )

        self.assertIn(
            "user",
            first_entry,
        )

        self.assertIn(
            "xp",
            first_entry,
        )

        self.assertIn(
            "id",
            first_entry["user"],
        )

        self.assertIn(
            "username",
            first_entry["user"],
        )

    def test_leaderboard_unauthorized(self):
        client = APIClient()

        response = client.get(
            "/api/leaderboard/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "UNAUTHORIZED",
        )

    # ============================================================
    # HEART REFILL API
    # ============================================================

    def test_heart_refill(self):
        self.user.stats.hearts = 2
        self.user.stats.save(
            update_fields=["hearts"]
        )

        response = self.client.post(
            "/api/practice/hearts/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        self.assertTrue(
            body["success"]
        )

        self.assertEqual(
            body["hearts"]["current"],
            5,
        )

        self.assertEqual(
            body["hearts"]["max"],
            5,
        )

    def test_heart_refill_when_already_full(self):
        self.user.stats.hearts = 5
        self.user.stats.save(
            update_fields=["hearts"]
        )

        response = self.client.post(
            "/api/practice/hearts/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        body = response.json()

        self.assertTrue(
            body["success"]
        )

        self.assertEqual(
            body["hearts"]["current"],
            5,
        )

        self.assertEqual(
            body["hearts"]["max"],
            5,
        )

    def test_heart_refill_unauthorized(self):
        client = APIClient()

        response = client.post(
            "/api/practice/hearts/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.json()["error"]["code"],
            "UNAUTHORIZED",
        )