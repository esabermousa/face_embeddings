# Standard Library
import os

# Django
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile

# Third Parties
import face_recognition

# Face Embeddings
from face_images.models import FaceImage


class FaceImageEncodingService:
    """Store & Encode Face Image."""

    def __init__(self, image_data: InMemoryUploadedFile) -> None:
        self.image_path = self._store_image(image_data)

    def _store_image(self, image_data: InMemoryUploadedFile) -> str:
        """Create a unique name and save image into Storage Dir.

        Note:Images Storage may be local Dir "Media" or S3

        Args:
            image (InMemoryUploadedFile): Uploaded image from request

        Returns:
            str: Stored Image path
        """
        image_name = default_storage.get_available_name(image_data.name)
        image_path = os.path.join(settings.MEDIA_ROOT, image_name)
        default_storage.save(image_path, image_data)
        return image_path

    def perform(self) -> FaceImage:
        """Load image file into face_recognition & extract encoded_face Then
        store into DB.

        Returns:
            FaceImage: Created record for FaceImage
        """
        loaded_image = face_recognition.load_image_file(self.image_path)
        encoding_results = face_recognition.face_encodings(loaded_image)
        encoded_face, status = (
            (encoding_results[0], FaceImage.ENCODE_SUCCESS) if encoding_results else (b"", FaceImage.ENCODE_FAILED)
        )
        face_image = FaceImage.objects.create(
            image_url=self.image_path, face_encoding=encoded_face, encoding_status=status
        )
        return face_image
