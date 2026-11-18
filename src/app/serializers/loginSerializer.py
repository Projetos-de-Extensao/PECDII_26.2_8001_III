from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Define as credenciais recebidas no login."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    """Define os dados retornados após autenticação bem-sucedida."""

    token = serializers.CharField()
    usuario_id = serializers.IntegerField()
    username = serializers.CharField()
