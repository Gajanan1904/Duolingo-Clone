from rest_framework import serializers



class ExerciseResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.ChoiceField(
        choices=[
            "multiple_choice",
            "translate",
            "word_bank",
            "match_pairs",
            "fill_blank",
            "type_answer",
        ]
    )
    question = serializers.CharField()
    data = serializers.JSONField()
    order = serializers.IntegerField()


class LessonResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    skill_id = serializers.IntegerField()
    xp_reward = serializers.IntegerField()
    total_exercises = serializers.IntegerField()
    exercises = ExerciseResponseSerializer(many=True)


class AnswerPayloadSerializer(serializers.Serializer):
    value = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    words = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    pairs = serializers.DictField(
        child=serializers.CharField(),
        required=False,
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "Answer must contain value, words, or pairs."
            )

        return attrs


class SubmitAnswerRequestSerializer(serializers.Serializer):
    exercise_id = serializers.IntegerField(min_value=1)
    answer = AnswerPayloadSerializer()


class FeedbackSerializer(serializers.Serializer):
    message = serializers.CharField()


class HeartsSerializer(serializers.Serializer):
    current = serializers.IntegerField(min_value=0)
    max = serializers.IntegerField(min_value=0)


class LessonStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            "in_progress",
            "completed",
            "failed",
        ]
    )


class SubmitAnswerResponseSerializer(serializers.Serializer):
    correct = serializers.BooleanField()
    exercise_id = serializers.IntegerField()
    attempt_id = serializers.IntegerField(min_value=1)
    feedback = FeedbackSerializer()
    hearts = HeartsSerializer()
    lesson = LessonStatusSerializer()


class CompleteLessonRequestSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField(min_value=1)


class CompletionLessonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=[
            "in_progress",
            "completed",
            "failed",
        ]
    )


class CompletionRewardsSerializer(serializers.Serializer):
    xp_earned = serializers.IntegerField(min_value=0)


class CompletionSkillSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    progress = serializers.IntegerField(min_value=0, max_value=100)
    crowns = serializers.IntegerField(min_value=0)
    status = serializers.ChoiceField(
        choices=[
            "locked",
            "available",
            "in_progress",
            "completed",
        ]
    )


class CompletionStatsSerializer(serializers.Serializer):
    total_xp = serializers.IntegerField(min_value=0)
    daily_xp = serializers.IntegerField(min_value=0)
    daily_xp_goal = serializers.IntegerField(min_value=0)
    current_streak = serializers.IntegerField(min_value=0)
    hearts = serializers.IntegerField(min_value=0)


class CompleteLessonResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    lesson = CompletionLessonSerializer()
    rewards = CompletionRewardsSerializer()
    skill = CompletionSkillSerializer()
    stats = CompletionStatsSerializer()