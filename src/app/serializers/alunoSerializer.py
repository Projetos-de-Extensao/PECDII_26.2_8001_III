from rest_framework import serializers

from .usuarioSerializer import UsuarioSerializer
from .responsavelSerializer import ResponsavelSerializer

from app.models import Aluno
from app.models import Responsavel


class AlunoSerializer(UsuarioSerializer):
    """Serializa alunos reutilizando as validações de usuário."""

    responsavel_id = serializers.PrimaryKeyRelatedField(
        queryset=Responsavel.objects.all(),
        required=False,
        write_only=True,
    )

    novo_responsavel = ResponsavelSerializer(
        required=False,
        write_only=True,
    )

    class Meta(UsuarioSerializer.Meta):
        model = Aluno
        fields = UsuarioSerializer.Meta.fields + [
            "matricula",
            "responsavel",
            "creditos",
            "responsavel_id",
            "novo_responsavel",
        ]
        read_only_fields = ["id", "creditos", "matricula"]

    def get_fields(self):
        """Restringe os campos editáveis pelo responsável."""
        fields = super().get_fields()
        # Alunos não possuem senha de acesso.
        fields.pop("password", None)
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

    def validate(self, attrs):
        """Valida o cadastro sem exigir senha do aluno."""
        if "responsavel_id" in attrs and "novo_responsavel" in attrs:
            raise serializers.ValidationError(
                "Informe um responsável existente ou um novo, não ambos."
            )

        return attrs

    def create(self, validated_data):
        """Cria aluno, matrícula e vínculo com responsável em uma transação."""
        from uuid import uuid4
        from django.db import transaction

        responsavel = validated_data.pop("responsavel_id", None)
        dados_responsavel = validated_data.pop("novo_responsavel", None)
        validated_data.pop("matricula", None)

        with transaction.atomic():
            # Cadastra o responsável novo, quando informado.
            if dados_responsavel is not None:
                serializer = ResponsavelSerializer()
                responsavel = serializer.create(dados_responsavel)

            # Cadastra o aluno com matrícula automática.
            aluno = Aluno.objects.create_user(
                **validated_data,
                matricula=f"TEMP-{uuid4().hex}",
            )
            aluno.set_unusable_password()
            aluno.matricula = f"MAT-{aluno.pk:06d}"
            aluno.save(update_fields=["matricula", "password"])

            # Vincula o aluno ao responsável.
            if responsavel is not None:
                responsavel.adicionarDependente(aluno)

        return aluno