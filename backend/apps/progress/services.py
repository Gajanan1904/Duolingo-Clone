from django.db import transaction

from apps.courses.models import Skill
from apps.progress.models import SkillProgress


class ProgressService:
    """Business logic for learner skill progression and unlocking."""

    SKILL_STATUS_LOCKED = "locked"
    SKILL_STATUS_AVAILABLE = "available"
    SKILL_STATUS_IN_PROGRESS = "in_progress"
    SKILL_STATUS_COMPLETED = "completed"

    @staticmethod
    def get_learning_path(user):
        """
        Return the complete learning path with learner-specific
        progress and skill statuses.
        """

        skill_progress = (
            SkillProgress.objects
            .filter(user=user)
            .select_related("skill__unit__course")
            .order_by(
                "skill__unit__course_id",
                "skill__unit__order",
                "skill__order",
            )
            .first()
        )

        if skill_progress:
            course = skill_progress.skill.unit.course
        else:
            first_skill = (
                Skill.objects
                .select_related("unit__course")
                .order_by(
                    "unit__course_id",
                    "unit__order",
                    "order",
                )
                .first()
            )

            course = first_skill.unit.course if first_skill else None

        if not course:
            return {
                "course": None,
                "units": [],
            }

        units = (
            course.units
            .prefetch_related("skills")
            .order_by("order")
        )

        result_units = []

        for unit in units:
            result_skills = []

            for skill in unit.skills.all():
                skill_progress, _ = SkillProgress.objects.get_or_create(
                    user=user,
                    skill=skill,
                    defaults={
                        "progress": 0,
                        "crowns": 0,
                        "status": ProgressService.calculate_skill_status(
                            user,
                            skill,
                        ),
                    },
                )

                status = ProgressService.calculate_skill_status(
                    user,
                    skill,
                )

                if skill_progress.status != status:
                    skill_progress.status = status
                    skill_progress.save(
                        update_fields=["status", "updated_at"]
                    )

                total_lessons = skill.lessons.count()

                completed_lessons = 0

                for lesson in skill.lessons.all():
                    if lesson.attempts.filter(
                        user=user,
                        status="completed",
                    ).exists():
                        completed_lessons += 1

                # Collect lesson IDs for this skill in order
                lesson_ids = list(
                    skill.lessons
                    .order_by("order")
                    .values_list("id", flat=True)
                )

                result_skills.append(
                    {
                        "id": skill.id,
                        "title": skill.title,
                        "description": skill.description,
                        "order": skill.order,
                        "status": status,
                        "progress": skill_progress.progress,
                        "crowns": skill_progress.crowns,
                        "total_lessons": total_lessons,
                        "completed_lessons": completed_lessons,
                        "lesson_ids": lesson_ids,
                    }
                )

            result_units.append(
                {
                    "id": unit.id,
                    "title": unit.title,
                    "description": unit.description,
                    "order": unit.order,
                    "skills": result_skills,
                }
            )

        return {
            "course": {
                "id": course.id,
                "name": course.name,
                "source_language": course.source_language,
                "target_language": course.target_language,
            },
            "units": result_units,
        }

    @staticmethod
    def calculate_skill_status(user, skill):
        """
        Determine the learner's current status for a skill
        using the skill's position within the course.
        """

        skill_progress = SkillProgress.objects.filter(
            user=user,
            skill=skill,
        ).first()

        if (
            skill_progress
            and skill_progress.status
            == ProgressService.SKILL_STATUS_COMPLETED
        ):
            return ProgressService.SKILL_STATUS_COMPLETED

        if skill_progress and skill_progress.progress > 0:
            return ProgressService.SKILL_STATUS_IN_PROGRESS

        previous_skill = (
            Skill.objects
            .filter(
                unit__course=skill.unit.course,
                unit__order=skill.unit.order,
                order__lt=skill.order,
            )
            .order_by("-order")
            .first()
        )

        if previous_skill is None:
            previous_skill = (
                Skill.objects
                .filter(
                    unit__course=skill.unit.course,
                    unit__order__lt=skill.unit.order,
                )
                .order_by("-unit__order", "-order")
                .first()
            )

        if previous_skill is None:
            return ProgressService.SKILL_STATUS_AVAILABLE

        previous_progress = SkillProgress.objects.filter(
            user=user,
            skill=previous_skill,
        ).first()

        if (
            previous_progress
            and previous_progress.status
            == ProgressService.SKILL_STATUS_COMPLETED
        ):
            return ProgressService.SKILL_STATUS_AVAILABLE

        return ProgressService.SKILL_STATUS_LOCKED

    @staticmethod
    @transaction.atomic
    def update_skill_progress(
        user,
        skill,
        progress=None,
        crowns=None,
    ):
        """
        Update learner progress for a skill while keeping values
        within valid bounds.
        """

        skill_progress, _ = (
            SkillProgress.objects
            .select_for_update()
            .get_or_create(
                user=user,
                skill=skill,
                defaults={
                    "progress": 0,
                    "crowns": 0,
                    "status": ProgressService.calculate_skill_status(
                        user,
                        skill,
                    ),
                },
            )
        )

        if progress is not None:
            skill_progress.progress = max(
                0,
                min(100, progress),
            )

        if crowns is not None:
            skill_progress.crowns = max(0, crowns)

        if skill_progress.progress >= 100:
            skill_progress.progress = 100
            skill_progress.status = (
                ProgressService.SKILL_STATUS_COMPLETED
            )

        elif skill_progress.progress > 0:
            skill_progress.status = (
                ProgressService.SKILL_STATUS_IN_PROGRESS
            )

        else:
            skill_progress.status = (
                ProgressService.calculate_skill_status(
                    user,
                    skill,
                )
            )

        skill_progress.save()

        return skill_progress

    @staticmethod
    @transaction.atomic
    def unlock_next_skill(user, skill):
        """
        Unlock the next skill in course progression after the
        supplied skill is completed.
        """

        current_status = (
            ProgressService.calculate_skill_status(
                user,
                skill,
            )
        )

        if current_status != ProgressService.SKILL_STATUS_COMPLETED:
            return None

        next_skill = (
            Skill.objects
            .filter(
                unit__course=skill.unit.course,
                unit__order=skill.unit.order,
                order__gt=skill.order,
            )
            .order_by("order")
            .first()
        )

        if next_skill is None:
            next_skill = (
                Skill.objects
                .filter(
                    unit__course=skill.unit.course,
                    unit__order__gt=skill.unit.order,
                )
                .order_by("unit__order", "order")
                .first()
            )

        if next_skill is None:
            return None

        next_progress, _ = (
            SkillProgress.objects.get_or_create(
                user=user,
                skill=next_skill,
                defaults={
                    "progress": 0,
                    "crowns": 0,
                    "status": (
                        ProgressService.SKILL_STATUS_AVAILABLE
                    ),
                },
            )
        )

        if next_progress.progress == 0:
            next_progress.status = (
                ProgressService.SKILL_STATUS_AVAILABLE
            )
            next_progress.save(
                update_fields=["status", "updated_at"]
            )

        return next_progress