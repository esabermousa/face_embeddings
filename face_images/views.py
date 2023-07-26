# Standard Library
import logging

# Django
from django.apps import apps
from django.shortcuts import get_object_or_404

# Third Parties
from drf_spectacular.utils import extend_schema
from request_logging.decorators import no_logging
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

# Face Embeddings
from common.fields import FaceEncodedField
from face_images.services import FaceImageEncodingService, FaceImageStatsService

logger = logging.getLogger("main_logger")


class FaceImageCreateView(APIView):
    class InputSerializer(serializers.Serializer):
        face_image = serializers.ImageField()

    class OutputSerializer(serializers.Serializer):
        public_id = serializers.CharField()
        face_encoding = FaceEncodedField()
        encoding_status = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    @extend_schema(
        operation_id="Face Image Encoding",
        tags=["Face Image"],
        request=InputSerializer,
        responses={201: OutputSerializer},
    )
    @no_logging(log_response=False)
    def post(self, request):
        """Encode Face Image & Retrieve encoded face."""
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        face_image_data = input_serializer.validated_data["face_image"]

        face_image_encoder = FaceImageEncodingService(face_image_data)
        face_image = face_image_encoder.perform()

        response_serializer = self.OutputSerializer(face_image)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class FaceImageDetailView(APIView):
    class OutputSerializer(serializers.Serializer):
        face_encoding = FaceEncodedField()
        encoding_status = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    @extend_schema(
        operation_id="Retrieve Encode Face Image",
        tags=["Face Image"],
        responses={200: OutputSerializer},
    )
    @no_logging(log_response=False)
    def get(self, request, public_id):
        """Gets Face Image Details."""
        face_image = get_object_or_404(apps.get_model("face_images.FaceImage"), public_id=public_id)
        response_serializer = self.OutputSerializer(face_image)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class FaceImageStatsView(APIView):
    class OutputSerializer(serializers.Serializer):
        encoding_status = serializers.CharField()
        count = serializers.IntegerField()

    @extend_schema(
        operation_id="Retrieve Stats Face Image",
        tags=["Face Image"],
        responses={200: OutputSerializer},
    )
    def get(self, request):
        """Retrieve the total number of processed images with its status."""
        status_stats = FaceImageStatsService.get_status_stats()
        response_serializer = self.OutputSerializer(status_stats, many=True)
        return Response(response_serializer.data)


class FaceImageEncodingAverageView(APIView):
    class OutputSerializer(serializers.Serializer):
        average_face_encoding = serializers.ListField(child=serializers.FloatField())

    @extend_schema(
        operation_id="Retrieve Average Face encodings",
        tags=["Face Image"],
        responses={200: OutputSerializer},
    )
    @no_logging(log_response=False)
    def get(self, request):
        """Retrieve the average of total success encoding images."""
        encodings_average = FaceImageStatsService.get_faces_encoding_average()
        response_serializer = self.OutputSerializer({"average_face_encoding": encodings_average})
        return Response(response_serializer.data)
