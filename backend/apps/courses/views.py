from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.serializers import LearningPathResponseSerializer
from apps.progress.services import ProgressService
from drf_spectacular.utils import extend_schema


class LearningPathAPIView(APIView):
    """
    Return the authenticated learner's learning path.
    """
    @extend_schema(
    responses={200: LearningPathResponseSerializer},
    )
    def get(self, request):
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

        path = ProgressService.get_learning_path(
            request.user
        )

        serializer = LearningPathResponseSerializer(
            path
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )