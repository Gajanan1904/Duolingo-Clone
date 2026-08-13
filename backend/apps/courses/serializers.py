from rest_framework import serializers


class CourseResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    source_language = serializers.CharField()
    target_language = serializers.CharField()


class SkillResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=[
            "locked",
            "available",
            "in_progress",
            "completed",
        ]
    )
    progress = serializers.IntegerField()
    crowns = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    lesson_ids = serializers.ListField(
        child=serializers.IntegerField(),
        default=list,
    )


class UnitResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    order = serializers.IntegerField()
    skills = SkillResponseSerializer(many=True)


class LearningPathResponseSerializer(serializers.Serializer):
    course = CourseResponseSerializer(allow_null=True)
    units = UnitResponseSerializer(many=True)