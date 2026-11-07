
from app.models import Responsavel
from .usuarioSerializer import UsuarioSerializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


class ResponsavelSerializer(UsuarioSerializer):
    """Serializa os dados do responsável e seus dependentes."""

    dependentes = serializers.SerializerMethodField()

    def get_dependentes(self, obj):
        """Retorna os IDs dos alunos vinculados ao responsável."""
        return list(obj.dependentes.values_list("aluno_id", flat=True))

    
    password = serializers.CharField(
        required=False,
        write_only=True,
        validators=[validate_password],
    )

    class Meta(UsuarioSerializer.Meta):
        model = Responsavel
        fields = UsuarioSerializer.Meta.fields + ["dependentes"]
        read_only_fields = ["id", "dependentes"]

    def create(self, validated_data):
        """Cria responsável com senha ou aguardando ativação."""
        senha = validated_data.pop("password", None)
        responsavel = Responsavel(**validated_data)

        if senha:
            responsavel.set_password(senha)
        else:
            responsavel.set_unusable_password()

        responsavel.save()
        return responsavel

    def validate(self, attrs):
        """Permite cadastro sem senha para ativação por convite."""
        return attrs
