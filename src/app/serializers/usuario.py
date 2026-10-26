from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from app.models.usuario import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"}
    )

    class Meta:
        model = Usuario
        fields = [
            "id",
            "nome_completo",
            "nome_usuario",
            "perfil",
            "senha",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if self.instance is None:
            if not attrs.get("senha"):
                raise serializers.ValidationError({
                    "senha": "A senha é obrigatória no cadastro."
                })

            if User.objects.filter(
                username=attrs["nome_usuario"]
            ).exists():
                raise serializers.ValidationError({
                    "nome_usuario": "Este nome de usuário já existe."
                })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        senha = validated_data.pop("senha")

        conta = User.objects.create_user(
            username=validated_data["nome_usuario"],
            password=senha
        )

        usuario = Usuario.objects.create(
            conta=conta,
            **validated_data
        )

        return usuario

    @transaction.atomic
    def update(self, instance, validated_data):
        senha = validated_data.pop("senha", None)

        novo_username = validated_data.get(
            "nome_usuario", instance.nome_usuario
        )

        if instance.conta:
            if User.objects.filter(
                username=novo_username
            ).exclude(pk=instance.conta.pk).exists():
                raise serializers.ValidationError({
                    "nome_usuario": "Este nome de usuário já existe."
                })

            instance.conta.username = novo_username

            if senha:
                instance.conta.set_password(senha)

            instance.conta.save()

        elif senha:
            raise serializers.ValidationError({
                "senha": "Este perfil não possui uma conta vinculada."
            })

        return super().update(instance, validated_data)