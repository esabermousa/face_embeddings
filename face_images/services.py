# Standard Library
import logging
import os

# Django
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Count

# Third Parties
import face_recognition
import numpy as np

# Face Embeddings
from face_images.models import FaceImage

logger = logging.getLogger("main_logger")


class FaceImageEncodingService:
    """Store & Encode Face Image."""

    def __init__(self, image_data: InMemoryUploadedFile) -> None:
        self.image_path = self._store_image(image_data)

    def _store_image(self, image_data: InMemoryUploadedFile) -> str:
        """Create a unique name and save image into Storage Dir.

        Note:Images Storage may be local dir "Media" or S3

        Args:
            image (InMemoryUploadedFile): Uploaded image from request

        Returns:
            str: Stored Image path
        """
        try:
            logger.info("Receiving Image and Starting store it...")
            image_name = default_storage.get_available_name(image_data.name)
            image_path = os.path.join(settings.MEDIA_ROOT, image_name)
            default_storage.save(image_path, image_data)
            logger.info("Storing Image successfully...")
            return image_path
        except Exception as exc:
            error_message = f"Exception occurred while file storing: {exc}"
            logger.warning(error_message, exc_info=True)
            raise ValidationError(error_message)

    def perform(self) -> FaceImage:
        """Load image file into face_recognition & extract encoded_face Then
        store into DB.

        Returns:
            FaceImage: Created record for FaceImage
        """
        try:
            logger.info("starting FaceImageEncoding Service...")
            loaded_image = face_recognition.load_image_file(self.image_path)
            encoding_results = face_recognition.face_encodings(loaded_image)
            encoded_face, status = (
                (encoding_results[0], FaceImage.ENCODE_SUCCESS) if encoding_results else (b"", FaceImage.ENCODE_FAILED)
            )
        except Exception as exc:
            error_message = f"Exception occurred while encoding face image: {exc}"
            logger.warning(error_message, exc_info=True)
            raise ValidationError(error_message)

        try:
            face_image = FaceImage.objects.create(
                image_url=self.image_path, face_encoding=encoded_face, encoding_status=status
            )
            logger.info(f"FaceImage: {face_image.public_id} encoded successfully...")
            return face_image
        except Exception as exc:
            error_message = f"Exception occurred while creating face image record: {exc}"
            logger.warning(error_message, exc_info=True)
            raise ValidationError(error_message)


class FaceImageStatsService:
    """Calculate Face Image stats."""

    @classmethod
    def get_status_stats(cls) -> list[dict]:
        """Return Stats for Face image status and its count.

        Returns:
            list: list of dict with encoding stats and its count
        """
        try:
            status_counts = FaceImage.objects.values("encoding_status").annotate(count=Count("encoding_status"))
            logger.info("Return images status stats successfully...")
            return status_counts
        except Exception as exc:
            error_message = f"Exception occurred while calculating face images status stats: {exc}"
            logger.warning(error_message, exc_info=True)
            raise ValidationError(error_message)

    @classmethod
    def get_faces_encoding_average(cls) -> list:
        """Retrieve all success encoded faces and calculate the average.

        Returns:
            list: Average face encoding
        """
        try:
            face_images = FaceImage.objects.filter(encoding_status=FaceImage.ENCODE_SUCCESS)
            if not face_images:
                error_message = "No face encodings found."
                logger.warning(error_message, exc_info=True)
                raise ValidationError(error_message)

            face_encodings = [np.frombuffer(encoding.face_encoding, dtype=float) for encoding in face_images]

            if len(face_encodings) < 2:
                error_message = "Insufficient face encodings to calculate average."
                logger.warning(error_message, exc_info=True)
                raise ValidationError(error_message)

            # Find the maximum shape among all face encodings
            max_shape = max(encoding.shape for encoding in face_encodings)

            # Adjust the shape of each face encoding to match the maximum shape
            face_encodings = [np.resize(encoding, max_shape) for encoding in face_encodings]

            # Calculate the average encoding
            average_encoding = np.mean(face_encodings, axis=0)

            return average_encoding.tolist()
        except Exception as exc:
            error_message = f"Exception occurred while calculating face encoding Average: {exc}"
            logger.warning(error_message, exc_info=True)
            raise ValidationError(error_message)
