# Generated by Django 4.1.10 on 2023-07-19 09:01

# Standard Library
import uuid

# Django
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FaceImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                (
                    "public_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                        verbose_name="Public ID",
                    ),
                ),
                ("image_url", models.URLField(verbose_name="Image URL")),
                ("face_encoding", models.BinaryField(verbose_name="Face Encoding")),
                (
                    "encoding_status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("SUCCESS", "Success"),
                            ("FAILED", "Failed"),
                        ],
                        default="PENDING",
                        max_length=20,
                        verbose_name="Encoding Status",
                    ),
                ),
            ],
            options={
                "verbose_name": "Face Image",
                "verbose_name_plural": "Face Images",
                "db_table": "face_image",
            },
        ),
        migrations.AddIndex(
            model_name="faceimage",
            index=models.Index(fields=["public_id"], name="face_image_public__310785_idx"),
        ),
    ]
