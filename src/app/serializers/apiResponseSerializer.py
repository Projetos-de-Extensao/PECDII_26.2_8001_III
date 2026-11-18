from rest_framework import serializers


class DetailResponseSerializer(serializers.Serializer):
    """Defines the standard detail message returned by simple API actions."""

    detail = serializers.CharField()
