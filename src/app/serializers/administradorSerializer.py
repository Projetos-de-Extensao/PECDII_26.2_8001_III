from rest_framework import serializers

from app.models import Administrador

from .alunoSerializer import AlunoSerializer
from .profissionalSerializer import (
    CadastroFisioterapeutaSerializer,
    CadastroNutricionistaSerializer,
    CadastroPsicologoSerializer,
    CadastroTreinadorSerializer,
    ProfissionalSerializer,
)
from .responsavelSerializer import ResponsavelSerializer
from .salaSerializer import SalaSerializer
from .usuarioSerializer import UsuarioSerializer


class AprovarSessaoResponseSerializer(serializers.Serializer):
    """Define a resposta da aprovação administrativa de sessão."""

    mensagem = serializers.CharField()
    sessao_id = serializers.IntegerField()
    status = serializers.CharField()


class DesaprovarSessaoResponseSerializer(AprovarSessaoResponseSerializer):
    """Define a resposta da desaprovação administrativa de sessão."""

    motivo = serializers.CharField()


class DesativarUsuarioResponseSerializer(serializers.Serializer):
    """Define a resposta da desativação administrativa de usuário."""

    mensagem = serializers.CharField()
    usuario_id = serializers.IntegerField()
    is_active = serializers.BooleanField()


class CadastrarSalaResponseSerializer(serializers.Serializer):
    """Define a resposta do cadastro administrativo de sala."""

    mensagem = serializers.CharField()
    sala = SalaSerializer()


class UsuarioCadastradoResponseSerializer(serializers.Serializer):
    """Define o resultado do cadastro de usuário comum."""

    mensagem = serializers.CharField()
    usuario = UsuarioSerializer()


class ProfissionalCadastradoResponseSerializer(serializers.Serializer):
    """Define o resultado do cadastro de profissional."""

    mensagem = serializers.CharField()
    usuario = ProfissionalSerializer()


class ResponsavelCadastradoResponseSerializer(serializers.Serializer):
    """Define o resultado do cadastro de responsável."""

    mensagem = serializers.CharField()
    usuario = ResponsavelSerializer()


class CreditosAlunoResponseSerializer(serializers.Serializer):
    """Define a resposta da atualização de créditos do aluno."""

    mensagem = serializers.CharField()
    aluno_id = serializers.IntegerField()
    creditos = serializers.IntegerField()


class AlunoDependenteCadastroSerializer(AlunoSerializer):
    """Defines dependent fields accepted within a responsible registration."""

    class Meta(AlunoSerializer.Meta):
        fields = [
            field
            for field in AlunoSerializer.Meta.fields
            if field not in {"responsavel", "responsavel_id", "novo_responsavel"}
        ]


class CadastroResponsavelAdminSerializer(ResponsavelSerializer):
    """Define o formato de cadastro de responsável pelo endpoint administrativo."""

    email = serializers.EmailField()
    dataNascimento = serializers.DateField()
    tipo = serializers.ChoiceField(choices=["responsavel"])
    alunos = AlunoDependenteCadastroSerializer(many=True, allow_empty=False)

    class Meta(ResponsavelSerializer.Meta):
        fields = [
            field
            for field in ResponsavelSerializer.Meta.fields
            if field not in {"password", "dependentes"}
        ] + ["tipo", "alunos"]


class CreditosAlunoSerializer(serializers.Serializer):
    """Define a quantidade de créditos a adicionar ou remover."""

    quantidade = serializers.IntegerField()


class AdministradorSerializer(UsuarioSerializer):
    """
    Serializa os dados de um administrador do PKZ Lab.

    Reutiliza os campos definidos em UsuarioSerializer,
    acrescentando o atributo tipoContrato, específico
    da classe Administrador.

    A serialização não inclui a senha do usuário,
    evitando sua exposição nas respostas da API.
    """

    class Meta(UsuarioSerializer.Meta):
        """
        Define o modelo e os campos utilizados
        na serialização de administradores.
        """

        model = Administrador

        # Reutiliza os campos de Usuario e adiciona tipoContrato.
        fields = UsuarioSerializer.Meta.fields + [
            'tipoContrato',
        ]