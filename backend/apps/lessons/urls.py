from django.urls import path

from apps.lessons.views import (
    CompleteLessonAPIView,
    LessonDetailAPIView,
    SubmitAnswerAPIView,
)


urlpatterns = [
    path(
        "lessons/<int:lesson_id>/",
        LessonDetailAPIView.as_view(),
        name="lesson-detail",
    ),
    path(
        "lessons/<int:lesson_id>/answer/",
        SubmitAnswerAPIView.as_view(),
        name="submit-answer",
    ),
    path(
        "lessons/<int:lesson_id>/complete/",
        CompleteLessonAPIView.as_view(),
        name="complete-lesson",
    ),
]