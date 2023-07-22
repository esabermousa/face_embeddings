# Django
from django.db import models
from django.utils.translation import gettext as _


class BaseModel(models.Model):
    """Parent class for all models."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    # META CLASS
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def queryset(self):
        """Returns a queryset of self object to be able to perform custom
        queries on it."""
        return self.__class__.objects.filter(id=self.id)
