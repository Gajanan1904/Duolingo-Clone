from django.urls import path

from apps.courses.views import LearningPathAPIView


urlpatterns = [
    path(
        "path/",
        LearningPathAPIView.as_view(),
        name="learning-path",
    ),
]