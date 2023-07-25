# Standard Library
import logging

# Django
from django.core.exceptions import RequestAborted
from django.db import connection

# Third Parties
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger("main_logger")


class HealthCheckView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def _check_db(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                logger.info("Database working.")
        except Exception as error:
            logger.critical(f"Can't connect to db. [Reason: {error}]", exc_info=True)
            raise RequestAborted("Database failure!")

    @extend_schema(
        auth=[],
        operation_id="Health-Check",
        tags=["Health Check"],
        responses={200: {}},
    )
    def get(self, request, *args, **kwargs):
        """Validate Service Health-check & its components."""
        try:
            logger.info("Starting health-check.")
            self._check_db()
            logger.info("health-check passed")
            return Response(status=status.HTTP_200_OK)
        except Exception as error:
            error_response = {"error": {"message": error.args[0], "extra": None}}
            return Response(error_response, status=status.HTTP_503_SERVICE_UNAVAILABLE)
