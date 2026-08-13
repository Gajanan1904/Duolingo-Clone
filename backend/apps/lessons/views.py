from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lessons.exceptions import (
    DomainError,
    LessonNotFoundError,
)
from apps.lessons.serializers import (
    CompleteLessonRequestSerializer,
    CompleteLessonResponseSerializer,
    LessonResponseSerializer,
    SubmitAnswerRequestSerializer,
    SubmitAnswerResponseSerializer,
)
from apps.lessons.services import LessonService
from apps.progress.models import LessonAttempt
from drf_spectacular.utils import extend_schema

class LessonDetailAPIView(APIView):
    """
    Return a playable lesson without exposing correct answers.
    """
    @extend_schema(
    responses={200: LessonResponseSerializer},
    )
    def get(self, request, lesson_id):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Authentication is required.",
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            lesson = LessonService.get_lesson(
                request.user,
                lesson_id,
            )
        except LessonNotFoundError:
            return Response(
                {
                    "error": {
                        "code": "LESSON_NOT_FOUND",
                        "message": "Lesson does not exist.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LessonResponseSerializer(lesson)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
        

class SubmitAnswerAPIView(APIView):
    """
    Submit one exercise answer for an active lesson attempt.
    """

    @extend_schema(
        request=SubmitAnswerRequestSerializer,
        responses={200: SubmitAnswerResponseSerializer},
    )
    def post(self, request, lesson_id):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Authentication is required.",
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = SubmitAnswerRequestSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                {
                    "error": {
                        "code": "INVALID_REQUEST",
                        "message": "Invalid request payload.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # The API contract has no separate start-lesson endpoint.
            # Therefore, initialize/reuse the active attempt here.
            attempt = LessonService.start_lesson(
                request.user,
                lesson_id,
            )

            result = LessonService.submit_answer(
                request.user,
                lesson_id,
                serializer.validated_data["exercise_id"],
                serializer.validated_data["answer"],
            )

            # Expose the active attempt ID so the frontend can
            # use it when calling the lesson completion endpoint.
            result["attempt_id"] = attempt.id

        except Exception as exc:
            return Response(
                {
                    "error": {
                        "code": getattr(
                            exc,
                            "code",
                            "INVALID_REQUEST",
                        ),
                        "message": getattr(
                            exc,
                            "message",
                            str(exc),
                        ),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        result["feedback"] = {
            "message": (
                "Correct!"
                if result["correct"]
                else "Not quite."
            )
        }

        response_serializer = SubmitAnswerResponseSerializer(
            result
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
        
class CompleteLessonAPIView(APIView):
    """
    Complete a lesson and return authoritative rewards/progress.
    """
    @extend_schema(
    request=CompleteLessonRequestSerializer,
    responses={200: CompleteLessonResponseSerializer},
)
    def post(self, request, lesson_id):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Authentication is required.",
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = CompleteLessonRequestSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                {
                    "error": {
                        "code": "INVALID_REQUEST",
                        "message": "Invalid request payload.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        attempt_id = serializer.validated_data["attempt_id"]

        try:
           

            attempt = LessonAttempt.objects.get(
                id=attempt_id,
                user=request.user,
            )

            result = LessonService.complete_lesson(
                request.user,
                lesson_id,
                attempt,
            )

        except LessonNotFoundError as exc:
            return Response(
                {
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except DomainError as exc:
            return Response(
                {
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except LessonAttempt.DoesNotExist:
            return Response(
                {
                    "error": {
                        "code": "INVALID_ATTEMPT",
                        "message": "Lesson attempt is invalid or unavailable.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = CompleteLessonResponseSerializer(
            result
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )