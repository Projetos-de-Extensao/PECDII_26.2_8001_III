from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Define as credenciais recebidas no login."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    usuario_id = serializers.IntegerField()
    username = serializers.CharField()


class LoginErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class LogoutResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class MeResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    nome = serializers.CharField()
    perfil = serializers.ChoiceField(
        choices=["administrador", "responsavel", "profissional", "usuario"]
    )
