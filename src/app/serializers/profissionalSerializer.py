from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from app.models import Profissional
from .usuarioSerializer import UsuarioSerializer
from app.models import Treinador, Fisioterapeuta, Psicologo, Nutricionista


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

    @extend_schema_field(serializers.CharField(allow_null=True))
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


class CadastroProfissionalSerializer(UsuarioSerializer):
    """Valida os dados de cadastro de profissionais especializados."""

    tipo = serializers.ChoiceField(
        choices=[
            "treinador",
            "fisioterapeuta",
            "psicologo",
            "nutricionista",
        ]
    )

    tipoContrato = serializers.CharField(max_length=100)
    formacao = serializers.CharField(max_length=255)

    especialidade = serializers.CharField(required=False)
    CREFITO = serializers.CharField(required=False)
    CRP = serializers.CharField(required=False)
    CRN = serializers.CharField(required=False)

    class Meta(UsuarioSerializer.Meta):
        model = Treinador
        fields = UsuarioSerializer.Meta.fields + [
            "tipo",
            "tipoContrato",
            "formacao",
            "especialidade",
            "CREFITO",
            "CRP",
            "CRN",
        ]

    def validate(self, attrs):
        """Exige o registro correspondente à especialização."""
        attrs = super().validate(attrs)

        campos = {
            "treinador": "especialidade",
            "fisioterapeuta": "CREFITO",
            "psicologo": "CRP",
            "nutricionista": "CRN",
        }

        campo = campos[attrs["tipo"]]

        if not attrs.get(campo):
            raise serializers.ValidationError({
                campo: "Campo obrigatório para esta especialização."
            })

        return attrs

    def create(self, validated_data):
        """Cria o profissional com sua especialização e senha protegida."""
        modelos = {
            "treinador": (Treinador, "especialidade"),
            "fisioterapeuta": (Fisioterapeuta, "CREFITO"),
            "psicologo": (Psicologo, "CRP"),
            "nutricionista": (Nutricionista, "CRN"),
        }

        tipo = validated_data.pop("tipo")
        modelo, campo = modelos[tipo]

        senha = validated_data.pop("password")
        especifico = validated_data.pop(campo)

        for outro_campo in ("especialidade", "CREFITO", "CRP", "CRN"):
            validated_data.pop(outro_campo, None)

        profissional = modelo(
            **validated_data,
            **{campo: especifico},
        )
        profissional.set_password(senha)
        profissional.full_clean()
        profissional.save()

        return profissional


class CadastroTreinadorSerializer(CadastroProfissionalSerializer):
    """Define os campos exclusivos do cadastro de treinador."""

    tipo = serializers.ChoiceField(choices=["treinador"])
    especialidade = serializers.CharField()


class CadastroFisioterapeutaSerializer(CadastroProfissionalSerializer):
    """Define os campos exclusivos do cadastro de fisioterapeuta."""

    tipo = serializers.ChoiceField(choices=["fisioterapeuta"])
    CREFITO = serializers.CharField()


class CadastroPsicologoSerializer(CadastroProfissionalSerializer):
    """Define os campos exclusivos do cadastro de psicólogo."""

    tipo = serializers.ChoiceField(choices=["psicologo"])
    CRP = serializers.CharField()


class CadastroNutricionistaSerializer(CadastroProfissionalSerializer):
    """Define os campos exclusivos do cadastro de nutricionista."""

    tipo = serializers.ChoiceField(choices=["nutricionista"])
    CRN = serializers.CharField()