
from app.models import Responsavel
from .usuarioSerializer import UsuarioSerializer
from rest_framework import serializers


class ResponsavelSerializer(UsuarioSerializer):
    """Serializa os dados do responsável e seus dependentes."""

    dependentes = serializers.SerializerMethodField()

    def get_dependentes(self, obj):
        """Retorna os IDs dos alunos vinculados ao responsável."""
        return list(obj.dependentes.values_list("aluno_id", flat=True))

    class Meta(UsuarioSerializer.Meta):
        model = Responsavel
        fields = UsuarioSerializer.Meta.fields + ["dependentes"]
        read_only_fields = ["id", "dependentes"]

    def create(self, validated_data):
        """Cria um responsável com senha protegida por hash."""
        senha = validated_data.pop("password")
        responsavel = Responsavel(**validated_data)
        responsavel.set_password(senha)
        responsavel.save()
        return responsavel
