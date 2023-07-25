# Django
from django.urls import include, path

# Face Embeddings
from api.views import HealthCheckView

urlpatterns = [
    path("health-check/", HealthCheckView.as_view(), name="health-check"),
    # Collections
    path("face-image/", include("face_images.urls")),
]
