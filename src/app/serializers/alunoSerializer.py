from rest_framework import serializers

from app.models import Aluno


class AlunoSerializer(serializers.ModelSerializer):
    """Converte os dados do aluno para a API."""

    class Meta:
        model = Aluno
        fields = [
            "id",
            "matricula",
            "responsavel",
            "creditos",
        ]
        read_only_fields = ["creditos"]