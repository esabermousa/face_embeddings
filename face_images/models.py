# Standard Library
import uuid

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# Face Embeddings
from common.models import BaseModel


class FaceImage(BaseModel):
    # CHOICES
    ENCODE_PENDING = "PENDING"
    ENCODE_SUCCESS = "SUCCESS"
    ENCODE_FAILED = "FAILED"
    ENCODE_STATUS_CHOICES = (
        (ENCODE_PENDING, "Pending"),
        (ENCODE_SUCCESS, "Success"),
        (ENCODE_FAILED, "Failed"),
    )

    # DATABASE FIELDS
    public_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Public ID"),
    )
    image_url = models.URLField(verbose_name=_("Image URL"), unique=True)
    face_encoding = models.BinaryField(verbose_name=_("Face Encoding"))
    encoding_status = models.CharField(
        choices=ENCODE_STATUS_CHOICES,
        default=ENCODE_PENDING,
        max_length=20,
        verbose_name=_("Encoding Status"),
    )

    # META CLASS
    class Meta:
        db_table = "face_image"
        verbose_name = "Face Image"
        verbose_name_plural = "Face Images"
        indexes = [
            models.Index(fields=["public_id"]),
        ]

    # BUILT_IN METHODS
    def __str__(self):
        return f"{self.public_id}"
