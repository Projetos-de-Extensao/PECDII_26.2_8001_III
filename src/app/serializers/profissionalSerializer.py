from rest_framework import serializers

from app.models import Profissional
from .usuarioSerializer import UsuarioSerializer


class ProfissionalSerializer(UsuarioSerializer):
    """Serializa os dados comuns e a especialização do profissional."""

    tipo = serializers.SerializerMethodField()

    class Meta(UsuarioSerializer.Meta):
        model = Profissional
        fields = UsuarioSerializer.Meta.fields + [
            "tipoContrato",
            "formacao",
            "tipo",
        ]
        read_only_fields = ["id", "tipo"]

    def get_tipo(self, obj):
        """Identifica a especialização cadastrada."""
        especializacoes = (
            "treinador",
            "fisioterapeuta",
            "psicologo",
            "nutricionista",
        )

        for tipo in especializacoes:
            if hasattr(obj, tipo):
                return tipo

        return None