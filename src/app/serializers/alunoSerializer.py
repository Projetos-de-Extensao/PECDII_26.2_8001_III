from app.models import Aluno
from .usuarioSerializer import UsuarioSerializer


class AlunoSerializer(UsuarioSerializer):
    """Serializa alunos reutilizando as validações de usuário."""

    class Meta(UsuarioSerializer.Meta):
        model = Aluno
        fields = UsuarioSerializer.Meta.fields + [
            "matricula",
            "responsavel",
            "creditos",
        ]
        read_only_fields = ["id", "creditos"]

    def create(self, validated_data):
        """Cria um aluno com senha protegida pelo Django."""
        return Aluno.objects.create_user(**validated_data)