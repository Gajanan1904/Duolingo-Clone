from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from apps.courses.models import Course, Unit, Skill
from apps.lessons.models import Lesson, Exercise
from apps.progress.models import SkillProgress
from apps.gamification.models import UserStats


class Command(BaseCommand):
    help = "Seed the Duolingo clone with deterministic demo data."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # ---------------------------------------------------------
        # DEMO USER
        # ---------------------------------------------------------
        user, created = User.objects.get_or_create(
            username="demo_user",
            defaults={
                "email": "demo@example.com",
                "first_name": "Demo",
                "last_name": "Learner",
                "is_active": True,
            },
        )

        if created:
            user.set_password("demo12345")
            user.save()

        # ---------------------------------------------------------
        # COURSE
        # ---------------------------------------------------------
        course, _ = Course.objects.update_or_create(
            code="ES",
            defaults={
                "name": "Spanish",
                "description": "Learn basic Spanish",
                "source_language": "English",
                "target_language": "Spanish",
                "is_active": True,
            },
        )

        # ---------------------------------------------------------
        # COURSE STRUCTURE
        # ---------------------------------------------------------
        structure = [
            {
                "title": "Basics",
                "description": "Learn basic Spanish",
                "order": 1,
                "skills": [
                    {
                        "title": "Greetings",
                        "description": "Basic greetings",
                        "order": 1,
                        "lesson": {
                            "title": "Basic Greetings",
                            "description": "Learn common Spanish greetings.",
                            "order": 1,
                        },
                    },
                    {
                        "title": "Introductions",
                        "description": "Introduce yourself in Spanish",
                        "order": 2,
                        "lesson": {
                            "title": "Basic Introductions",
                            "description": "Learn how to introduce yourself.",
                            "order": 1,
                        },
                    },
                ],
            },
            {
                "title": "Food",
                "description": "Learn Spanish words for food and drinks",
                "order": 2,
                "skills": [
                    {
                        "title": "Common Foods",
                        "description": "Common food vocabulary",
                        "order": 1,
                        "lesson": {
                            "title": "Common Foods",
                            "description": "Learn common Spanish food words.",
                            "order": 1,
                        },
                    },
                    {
                        "title": "Drinks",
                        "description": "Common drink vocabulary",
                        "order": 2,
                        "lesson": {
                            "title": "Drinks",
                            "description": "Learn common Spanish drink words.",
                            "order": 1,
                        },
                    },
                ],
            },
            {
                "title": "Everyday Life",
                "description": "Useful vocabulary for daily life",
                "order": 3,
                "skills": [
                    {
                        "title": "Family",
                        "description": "Family vocabulary",
                        "order": 1,
                        "lesson": {
                            "title": "Family",
                            "description": "Learn Spanish family vocabulary.",
                            "order": 1,
                        },
                    },
                    {
                        "title": "Daily Activities",
                        "description": "Everyday activities",
                        "order": 2,
                        "lesson": {
                            "title": "Daily Activities",
                            "description": "Learn Spanish vocabulary for daily activities.",
                            "order": 1,
                        },
                    },
                ],
            },
        ]

        skills_created = []

        for unit_data in structure:
            unit, _ = Unit.objects.update_or_create(
                course=course,
                order=unit_data["order"],
                defaults={
                    "title": unit_data["title"],
                    "description": unit_data["description"],
                },
            )

            for skill_data in unit_data["skills"]:
                skill, _ = Skill.objects.update_or_create(
                    unit=unit,
                    order=skill_data["order"],
                    defaults={
                        "title": skill_data["title"],
                        "description": skill_data["description"],
                    },
                )

                lesson_data = skill_data["lesson"]

                lesson, _ = Lesson.objects.update_or_create(
                    skill=skill,
                    order=lesson_data["order"],
                    defaults={
                        "title": lesson_data["title"],
                        "description": lesson_data["description"],
                        "xp_reward": 10,
                    },
                )

                skills_created.append(skill)

                self.create_exercises(lesson)

        # ---------------------------------------------------------
        # DEMO USER STATS
        # ---------------------------------------------------------
        UserStats.objects.update_or_create(
            user=user,
            defaults={
                "total_xp": 250,
                "current_streak": 5,
                "longest_streak": 5,
                "hearts": 4,
                "max_hearts": 5,
                "daily_xp_goal": 20,
                "daily_xp": 20,
            },
        )

        # ---------------------------------------------------------
        # DEMO SKILL PROGRESS
        # ---------------------------------------------------------
        for index, skill in enumerate(skills_created):
            if index == 0:
                progress = 100
                crowns = 3
                status = SkillProgress.SkillStatus.COMPLETED
            elif index == 1:
                progress = 40
                crowns = 2
                status = SkillProgress.SkillStatus.IN_PROGRESS
            else:
                progress = 0
                crowns = 0
                status = SkillProgress.SkillStatus.LOCKED

            SkillProgress.objects.update_or_create(
                user=user,
                skill=skill,
                defaults={
                    "progress": progress,
                    "crowns": crowns,
                    "status": status,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed completed successfully."
            )
        )

        self.stdout.write(
            f"Course: {Course.objects.count()}"
        )
        self.stdout.write(
            f"Units: {Unit.objects.count()}"
        )
        self.stdout.write(
            f"Skills: {Skill.objects.count()}"
        )
        self.stdout.write(
            f"Lessons: {Lesson.objects.count()}"
        )
        self.stdout.write(
            f"Exercises: {Exercise.objects.count()}"
        )

    # =============================================================
    # EXERCISES
    # =============================================================

    def create_exercises(self, lesson):
        exercises = [
            {
                "order": 1,
                "type": Exercise.ExerciseType.MULTIPLE_CHOICE,
                "question": "What does 'Hola' mean?",
                "data": {
                    "options": [
                        "Hello",
                        "Goodbye",
                        "Thanks",
                        "Please",
                    ]
                },
                "correct_answer": {
                    "value": "Hello"
                },
            },
            {
                "order": 2,
                "type": Exercise.ExerciseType.TRANSLATE,
                "question": "Translate: Hello",
                "data": {
                    "source_text": "Hello"
                },
                "correct_answer": {
                    "value": "Hola"
                },
            },
            {
                "order": 3,
                "type": Exercise.ExerciseType.WORD_BANK,
                "question": "Build the Spanish sentence",
                "data": {
                    "words": [
                        "Yo",
                        "como",
                        "una",
                        "manzana",
                    ]
                },
                "correct_answer": {
                    "words": [
                        "Yo",
                        "como",
                        "una",
                        "manzana",
                    ]
                },
            },
            {
                "order": 4,
                "type": Exercise.ExerciseType.MATCH_PAIRS,
                "question": "Match the words",
                "data": {
                    "pairs": [
                        {
                            "id": "1",
                            "left": "Hello",
                            "right": "Hola",
                        },
                        {
                            "id": "2",
                            "left": "Goodbye",
                            "right": "Adiós",
                        },
                    ]
                },
                "correct_answer": {
                    "pairs": {
                        "1": "Hola",
                        "2": "Adiós",
                    }
                },
            },
            {
                "order": 5,
                "type": Exercise.ExerciseType.FILL_BLANK,
                "question": "Yo ___ una manzana.",
                "data": {},
                "correct_answer": {
                    "value": "como"
                },
            },
            {
                "order": 6,
                "type": Exercise.ExerciseType.TYPE_ANSWER,
                "question": "Translate: Thank you",
                "data": {
                    "source_text": "Thank you"
                },
                "correct_answer": {
                    "value": "Gracias"
                },
            },
        ]

        for exercise_data in exercises:
            Exercise.objects.update_or_create(
                lesson=lesson,
                order=exercise_data["order"],
                defaults={
                    "type": exercise_data["type"],
                    "question": exercise_data["question"],
                    "data": exercise_data["data"],
                    "correct_answer": exercise_data["correct_answer"],
                },
            )