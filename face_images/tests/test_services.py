# Standard Library
import io
import os

# Django
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from django.test import TestCase

# Third Parties
from PIL import Image

# Face Embeddings
from face_images.models import FaceImage
from face_images.services import FaceImageEncodingService


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
