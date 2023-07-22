# Standard Library
import io
import os
import uuid

# Django
from django.conf import settings
from django.urls import reverse

# Third Parties
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

# Face Embeddings
from face_images.models import FaceImage


class FaceImageCreateViewTests(APITestCase):
    @classmethod
    def generate_image(cls):
        new_file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color="red")
        image.save(new_file, "png")
        new_file.name = "test.png"
        new_file.seek(0)
        return new_file

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("encode-face-image")
        cls.face_image = cls.generate_image()
        cls.request_data = {
            "face_image": cls.face_image,
        }

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

    def test_success_encode_face_image(self):
        response = self.client.post(data=self.request_data, path=self.url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FaceImage.objects.count(), 1)
        self.assertIn("public_id", response.data)
        self.assertIn("face_encoding", response.data)
        self.assertIn("encoding_status", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_encode_face_image_with_empty_body(self):
        response_message = "No file was submitted."
        response = self.client.post(data=dict(), path=self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("face_image", response.data)
        self.assertIn(response_message, response.data["face_image"])


class FaceImageDetailViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.face_record = FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test.png"))
        cls.url = reverse("retrieve-encode-face-image", args=[cls.face_record.public_id])

    @classmethod
    def tearDownClass(cls):
        FaceImage.objects.all().delete()

    def test_success_retrieve_encode_face_image(self):
        response = self.client.get(path=self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("face_encoding", response.data)
        self.assertIn("encoding_status", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_get_face_image_details_not_found(self):
        url = reverse("retrieve-encode-face-image", args=[str(uuid.uuid4())])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Not found.", response.data["detail"])


class FaceImageStatsViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test1.png"), encoding_status="SUCCESS")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test2.png"), encoding_status="PENDING")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test3.png"), encoding_status="SUCCESS")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test4.png"), encoding_status="SUCCESS")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test5.png"), encoding_status="FAILED")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test6.png"), encoding_status="PENDING")
        cls.url = reverse("retrieve-stats-face-image")

    @classmethod
    def tearDownClass(cls):
        FaceImage.objects.all().delete()

    def test_success_retrieve_stats_face_image(self):
        response = self.client.get(path=self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("encoding_status", response.data[0])
        self.assertIn("count", response.data[0])
        self.assertEqual(len(response.data), 3)

        status_counts = {entry["encoding_status"]: entry["count"] for entry in response.data}
        self.assertEqual(status_counts.get("SUCCESS"), 3)
        self.assertEqual(status_counts.get("PENDING"), 2)
        self.assertEqual(status_counts.get("FAILED"), 1)
