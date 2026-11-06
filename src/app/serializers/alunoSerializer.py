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

    def get_fields(self):
        """Restringe os campos editáveis pelo responsável."""
        fields = super().get_fields()
        request = self.context.get("request")

        if request and request.method == "PATCH":
            from app.permissions.administradorPermission import IsAdministrador

            if not IsAdministrador().has_permission(request, self.context["view"]):
                permitidos = {
                    "first_name",
                    "last_name",
                    "telefone",
                    "endereco",
                    "dataNascimento",
                }

                for nome, campo in fields.items():
                    if nome not in permitidos:
                        campo.read_only = True

        return fields

    def create(self, validated_data):
        """Cria um aluno com senha protegida pelo Django."""
        return Aluno.objects.create_user(**validated_data)