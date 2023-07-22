# Standard Library
import os

# Django
from django.apps import apps
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Count
from django.shortcuts import get_object_or_404

# Third Parties
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView


class FaceImageCreateView(APIView):
    class InputSerializer(serializers.Serializer):
        face_image = serializers.ImageField()

    class OutputSerializer(serializers.Serializer):
        public_id = serializers.CharField()
        face_encoding = serializers.SerializerMethodField()
        encoding_status = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

        def get_face_encoding(self, obj):
            # Custom logic to retrieve the face binary encoding
            return obj.face_encoding

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            face_image_data = serializer.validated_data["face_image"]

            # Generate a unique filename for the image
            filename = default_storage.get_available_name(face_image_data.name)

            # Save the image to the local directory using default storage
            filepath = default_storage.save(os.path.join(settings.MEDIA_ROOT, filename), face_image_data)

            # Save the face_image to the database
            face_image_model = apps.get_model("face_images.FaceImage")
            face_image = face_image_model.objects.create(image_url=os.path.join(settings.MEDIA_URL, filepath))

            # Serialize the created face_image and return the response
            response_serializer = self.OutputSerializer(face_image)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=400)


class FaceImageDetailView(APIView):
    class OutputSerializer(serializers.Serializer):
        face_encoding = serializers.SerializerMethodField()
        encoding_status = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

        def get_face_encoding(self, obj):
            # Custom logic to retrieve the face binary encoding
            return "".join(chr(byte) for byte in obj.face_encoding)

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
        status_counts_data = (
            apps.get_model("face_images.FaceImage")
            .objects.values("encoding_status")
            .annotate(count=Count("encoding_status"))
        )
        serializer = self.OutputSerializer(status_counts_data, many=True)
        return Response(serializer.data)
