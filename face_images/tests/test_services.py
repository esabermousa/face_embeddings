# Standard Library
import io
import os

# Django
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from django.test import TestCase

# Third Parties
import numpy as np
import pytest
from PIL import Image

# Face Embeddings
from face_images.models import FaceImage
from face_images.services import FaceImageEncodingService, FaceImageStatsService


class FaceImageEncodingServiceTests(TestCase):
    @classmethod
    def get_image_content(cls, file_path):
        with open(file_path, "rb") as f:
            return f.read()

    @classmethod
    def generate_fake_image(cls):
        image = Image.new("RGB", (100, 100), color="red")
        image_io = io.BytesIO()
        image.save(image_io, format="png")
        image_io.seek(0)
        image_file = InMemoryUploadedFile(image_io, None, "test.png", "image/png", image_io.getbuffer().nbytes, None)
        return image_file

    @classmethod
    def setUpTestData(cls) -> None:
        image_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_image.jpg")
        cls.face_image = SimpleUploadedFile(
            "test_image.jpg", cls.get_image_content(image_file_path), content_type="image/jpg"
        )
        cls.fake_image = cls.generate_fake_image()

    @classmethod
    def delete_image_file(cls):
        media_path = settings.MEDIA_ROOT
        for filename in os.listdir(media_path):
            if filename.startswith("test"):
                file_path = os.path.join(media_path, filename)
                os.remove(file_path)

    @classmethod
    def tearDownClass(cls):
        FaceImage.objects.all().delete()
        cls.delete_image_file()

    def test_face_image_encoding_service(self):
        service = FaceImageEncodingService(image_data=self.face_image)
        face_image = service.perform()

        self.assertIsInstance(face_image, FaceImage)
        self.assertEqual(face_image.image_url, service.image_path)
        self.assertEqual(face_image.encoding_status, FaceImage.ENCODE_SUCCESS)

    def test_image_stored_in_media(self):
        service = FaceImageEncodingService(image_data=self.face_image)
        stored_path = service._store_image(self.face_image)

        self.assertTrue(os.path.exists(stored_path))
        self.assertTrue(stored_path.startswith(settings.MEDIA_ROOT))

    def test_failed_image_encoding(self):
        service = FaceImageEncodingService(image_data=self.fake_image)
        face_image = service.perform()

        self.assertIsInstance(face_image, FaceImage)
        self.assertEqual(face_image.image_url, service.image_path)
        self.assertEqual(face_image.face_encoding, b"")
        self.assertEqual(face_image.encoding_status, FaceImage.ENCODE_FAILED)


class FaceImageStatsServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.face_encoding1 = np.array([0.5, -0.3, 0.7, 0.2, -0.1])
        cls.face_encoding2 = np.array([0.8, 0.1, -0.5, 0.4, 0.9])
        cls.face_encoding3 = np.array([-0.2, 0.6, 0.3, -0.4, 0.5])
        cls.face_encoding4 = np.array([0.1, 0.6, -0.1, 0.2, 0.7])
        cls.face_encoding5 = np.array([-0.5, 0.2, 0.3, -0.4, 0.5])
        cls.face_encoding6 = np.array([0.5, -0.3, 0.7, 0.2, -0.1])

        cls.face_image1 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test1.png"),
            face_encoding=cls.face_encoding1.tobytes(),
            encoding_status="SUCCESS",
        )
        cls.face_image2 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test2.png"),
            face_encoding=cls.face_encoding2.tobytes(),
            encoding_status="PENDING",
        )
        cls.face_image3 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test3.png"),
            face_encoding=cls.face_encoding3.tobytes(),
            encoding_status="SUCCESS",
        )
        cls.face_image4 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test4.png"),
            face_encoding=cls.face_encoding4.tobytes(),
            encoding_status="SUCCESS",
        )
        cls.face_image5 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test5.png"),
            face_encoding=cls.face_encoding5.tobytes(),
            encoding_status="FAILED",
        )
        cls.face_image6 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test6.png"),
            face_encoding=cls.face_encoding6.tobytes(),
            encoding_status="PENDING",
        )

    @classmethod
    def tearDownClass(cls):
        FaceImage.objects.all().delete()

    def test_get_status_stats(self):
        expected_status_counts = [
            {"encoding_status": "PENDING", "count": 2},
            {"encoding_status": "SUCCESS", "count": 3},
            {"encoding_status": "FAILED", "count": 1},
        ]

        status_counts = FaceImageStatsService.get_status_stats()

        sorted_expected_counts = sorted(expected_status_counts, key=lambda x: x["encoding_status"])
        sorted_actual_counts = sorted(status_counts, key=lambda x: x["encoding_status"])

        self.assertEqual(sorted_actual_counts, sorted_expected_counts)

    def test_calculate_average_face_encoding(self):
        average_face_encoding = FaceImageStatsService.get_faces_encoding_average()
        # Calculate the expected average face encoding
        expected_average_encoding = np.mean([self.face_encoding1, self.face_encoding3, self.face_encoding4], axis=0)

        # Check that the average face encoding returned in the response is equal to the expected average encoding
        self.assertListEqual(average_face_encoding, expected_average_encoding.tolist())

    def test_calculate_average_face_encoding_insufficient_face_encodings(self):
        # Delete all face encodings except one from the database
        self.face_image3.delete()
        self.face_image4.delete()

        with pytest.raises(Exception, match="Insufficient face encodings to calculate average."):
            FaceImageStatsService.get_faces_encoding_average()

    def test_calculate_average_face_encoding_no_face_encodings(self):
        # Delete all face encodings from the database
        FaceImage.objects.all().delete()

        with pytest.raises(Exception, match="No face encodings found."):
            FaceImageStatsService.get_faces_encoding_average()
