
from app.models import Responsavel
from .usuarioSerializer import UsuarioSerializer


class ResponsavelSerializer(UsuarioSerializer):
    """Serializa os dados do responsável e seus dependentes."""

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
