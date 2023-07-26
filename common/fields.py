# Standard Library
import base64

# Third Parties
from rest_framework import serializers


class FaceEncodedField(serializers.Field):
    def to_representation(self, value):
        return base64.b64encode(value).decode("utf-8")
