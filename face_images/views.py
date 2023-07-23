# Standard Library


# Django
from django.apps import apps
from django.shortcuts import get_object_or_404

# Third Parties
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

# Face Embeddings
from common.fields import FaceEncodedField
from face_images.services import FaceImageEncodingService, FaceImageStatsService


class FaceImageCreateView(APIView):
    class InputSerializer(serializers.Serializer):
        face_image = serializers.ImageField()

    class OutputSerializer(serializers.Serializer):
        public_id = serializers.CharField()
        face_encoding = FaceEncodedField()
        encoding_status = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def post(self, request):
        """Encode Face Image & Retrieve encoded face."""
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            face_image_data = serializer.validated_data["face_image"]

            face_image_encoder = FaceImageEncodingService(face_image_data)
            face_image = face_image_encoder.perform()

            response_serializer = self.OutputSerializer(face_image)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=400)


class FaceImageDetailView(APIView):
    class OutputSerializer(serializers.Serializer):
        face_encoding = FaceEncodedField()
        encoding_status = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def get(self, request, public_id):
        """Gets Face Image Details."""
        face_image = get_object_or_404(apps.get_model("face_images.FaceImage"), public_id=public_id)
        response_serializer = self.OutputSerializer(face_image)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class FaceImageStatsView(APIView):
    class OutputSerializer(serializers.Serializer):
        encoding_status = serializers.CharField()
        count = serializers.IntegerField()

    def get(self, request):
        """Retrieve the total number of processed images with its status."""
        status_stats = FaceImageStatsService.get_status_stats()
        serializer = self.OutputSerializer(status_stats, many=True)
        return Response(serializer.data)
