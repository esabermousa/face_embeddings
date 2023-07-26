# Django
from django.urls import include, path

# Third Parties
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Face Embeddings
from api.views import HealthCheckView

urlpatterns = [
    path("health-check/", HealthCheckView.as_view(), name="health-check"),
    # Collections
    path("face-image/", include("face_images.urls")),
    # API Doc Schema
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
