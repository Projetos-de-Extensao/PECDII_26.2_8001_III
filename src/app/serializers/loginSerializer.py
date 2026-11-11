from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Define as credenciais recebidas no login."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
