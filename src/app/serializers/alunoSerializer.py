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
        read_only_fields = ["id", "creditos", "matricula"]

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

    #def create(self, validated_data):
       # """Cria um aluno com senha protegida pelo Django."""
       # return Aluno.objects.create_user(**validated_data)

    def create(self, validated_data):
        """Cria o aluno e gera uma matrícula única automaticamente."""
        from django.db import transaction

        validated_data.pop("matricula", None)

        with transaction.atomic():
            aluno = Aluno.objects.create_user(
                **validated_data,
                matricula=f"TEMP-{__import__('uuid').uuid4().hex}",
            )
            aluno.matricula = f"MAT-{aluno.pk:06d}"
            aluno.save(update_fields=["matricula"])

        return aluno