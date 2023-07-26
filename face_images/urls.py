# Django
from django.urls import path

# Face Embeddings
from face_images.views import (
    FaceImageCreateView,
    FaceImageDetailView,
    FaceImageEncodingAverageView,
    FaceImageStatsView,
)

urlpatterns = [
    path("", FaceImageCreateView.as_view(), name="encode-face-image"),
    path("stats/", FaceImageStatsView.as_view(), name="retrieve-stats-face-image"),
    path("avg-encodings/", FaceImageEncodingAverageView.as_view(), name="retrieve-avg-face-encodings"),
    path("<uuid:public_id>/", FaceImageDetailView.as_view(), name="retrieve-encode-face-image"),
]
