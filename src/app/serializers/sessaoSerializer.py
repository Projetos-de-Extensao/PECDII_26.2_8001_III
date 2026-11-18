from rest_framework import serializers

from app.models import Sessao
from app.models import Sala, Profissional
from app.Enums import StatusPresenca


class MotivoSessaoSerializer(serializers.Serializer):
    """Define a justificativa para rejeitar ou cancelar uma sessão."""

    motivo = serializers.CharField(allow_blank=False, trim_whitespace=True)


class RegistrarPresencaSerializer(serializers.Serializer):
    """Define o status e a justificativa de uma presença."""

    status = serializers.ChoiceField(
        choices=[
            StatusPresenca.PRESENTE,
            StatusPresenca.AUSENTE,
            StatusPresenca.JUSTIFICADO,
        ]
    )
    justificativa = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

class SessaoSerializer(serializers.ModelSerializer):
    """Disponibiliza os dados da sessão para a API."""

    class Meta:
        model = Sessao
        fields = [
            "id",
            "sala",
            "profissional",
            "dataHora",
            "duracao",
            "status",
            "creditosNecessarios",
            "status",
            "motivoCancelamento",
            "creditosNecessarios",
        ]
        read_only_fields = fields


class SolicitacaoSessaoSerializer(serializers.Serializer):
    """Valida os dados necessários para solicitar uma sessão."""

    sala = serializers.PrimaryKeyRelatedField(
        queryset=Sala.objects.all()
    )
    profissional = serializers.PrimaryKeyRelatedField(
        queryset=Profissional.objects.all(),
        required=False,
    )
    dataHora = serializers.DateTimeField()
    duracao = serializers.DurationField()
    creditosNecessarios = serializers.IntegerField(min_value=0)