from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from rest_framework.decorators import action

from app.models import Sessao
from app.serializers import SessaoSerializer
from app.models import Administrador, Profissional
from app.serializers.sessaoSerializer import SolicitacaoSessaoSerializer


class SessaoView(ModelViewSet):
    """Permite consultar as sessões cadastradas."""

    def get_queryset(self):
        """Filtra sessões por data, profissional, sala e status."""
        queryset = Sessao.objects.select_related(
            "sala", "profissional"
        ).all().order_by("dataHora")

        params = self.request.query_params

        if params.get("data"):
            from datetime import date

            try:
                date.fromisoformat(params["data"])
            except ValueError:
                raise ValidationError({
                    "data": "Informe uma data válida no formato AAAA-MM-DD."
                })

        for campo in ("profissional", "sala"):
            if params.get(campo) and not params[campo].isdigit():
                raise ValidationError({
                    campo: "Informe um ID numérico válido."
                })

        if params.get("status"):
            status_validos = [valor for valor, _ in Sessao._meta.get_field("status").choices]

            if params["status"] not in status_validos:
                raise ValidationError({
                    "status": "Status de sessão inválido."
                })

        if params.get("data"):
            queryset = queryset.filter(dataHora__date=params["data"])

        if params.get("profissional"):
            queryset = queryset.filter(profissional_id=params["profissional"])

        if params.get("sala"):
            queryset = queryset.filter(sala_id=params["sala"])

        if params.get("status"):
            queryset = queryset.filter(status=params["status"])

        return queryset

    serializer_class = SessaoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def create(self, request, *args, **kwargs):
        """Solicita uma sessão conforme o perfil autenticado."""
        dados = SolicitacaoSessaoSerializer(data=request.data)
        dados.is_valid(raise_exception=True)

        valores = dados.validated_data
        usuario = request.user

        if Administrador.objects.filter(pk=usuario.pk).exists():
            profissional = valores.get("profissional")

            if profissional is None:
                raise serializers.ValidationError({
                    "profissional": "Informe o profissional responsável."
                })

        elif Profissional.objects.filter(pk=usuario.pk).exists():
            profissional = Profissional.objects.get(pk=usuario.pk)

            if (
                valores.get("profissional") is not None
                and valores["profissional"].pk != profissional.pk
            ):
                raise PermissionDenied(
                    "Você só pode solicitar sessões para si mesmo."
                )
        else:
            raise PermissionDenied(
                "Seu perfil não pode solicitar sessões."
            )

        try:
            sessao = Sessao.solicitar(
                profissional=profissional,
                sala=valores["sala"],
                dataHora=valores["dataHora"],
                duracao=valores["duracao"],
                creditosNecessarios=valores["creditosNecessarios"],
            )
        except DjangoValidationError as erro:
            return Response(
                {"erro": erro.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            SessaoSerializer(sessao).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):
        """Permite ao administrador confirmar uma sessão solicitada."""
        if not Administrador.objects.filter(pk=request.user.pk).exists():
            raise PermissionDenied(
                "Apenas administradores podem confirmar sessões."
            )

        sessao = self.get_object()

        try:
            sessao.confirmar()
        except DjangoValidationError as erro:
            raise serializers.ValidationError({"erro": erro.messages})

        return Response(SessaoSerializer(sessao).data)

    @action(detail=True, methods=["post"])
    def rejeitar(self, request, pk=None):
        """Permite ao administrador rejeitar uma sessão."""
        if not Administrador.objects.filter(pk=request.user.pk).exists():
            raise PermissionDenied(
                "Apenas administradores podem rejeitar sessões."
            )

        motivo = request.data.get("motivo", "")
        if not isinstance(motivo, str) or not motivo.strip():
            raise serializers.ValidationError({
                "motivo": "Informe o motivo da rejeição."
            })

        sessao = self.get_object()

        try:
            sessao.rejeitar(motivo)
        except DjangoValidationError as erro:
            raise serializers.ValidationError({"erro": erro.messages})

        return Response(SessaoSerializer(sessao).data)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """Permite cancelar uma sessão conforme o perfil autorizado."""
        usuario = request.user
        sessao = self.get_object()

        administrador = Administrador.objects.filter(pk=usuario.pk).exists()
        profissional = Profissional.objects.filter(pk=usuario.pk).exists()

        if not administrador and not (
            profissional and sessao.profissional_id == usuario.pk
        ):
            raise PermissionDenied(
                "Você não tem permissão para cancelar esta sessão."
            )

        motivo = request.data.get("motivo", "")

        if not isinstance(motivo, str) or not motivo.strip():
            raise serializers.ValidationError({
                "motivo": "Informe o motivo do cancelamento."
            })

        try:
            sessao.cancelar(motivo)
        except DjangoValidationError as erro:
            raise serializers.ValidationError({"erro": erro.messages})

        return Response(SessaoSerializer(sessao).data)