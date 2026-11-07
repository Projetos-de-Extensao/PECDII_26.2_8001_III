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
from app.models import Presenca
from app.Enums import StatusPresenca, StatusSessao


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
    http_method_names = ["get", "post", "patch", "head", "options"]

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

    @action(detail=True, methods=["patch"], url_path=r"presencas/(?P<aluno_id>[0-9]+)")
    def registrar_presenca(self, request, pk=None, aluno_id=None):
        """Registra presença, ausência ou justificativa de um aluno."""
        sessao = self.get_object()
        usuario = request.user

        administrador = Administrador.objects.filter(pk=usuario.pk).exists()
        profissional_responsavel = (
            Profissional.objects.filter(pk=usuario.pk).exists()
            and sessao.profissional_id == usuario.pk
        )

        if not administrador and not profissional_responsavel:
            raise PermissionDenied(
                "Apenas o profissional responsável ou um administrador "
                "pode registrar presenças nesta sessão."
            )

        presenca = Presenca.objects.filter(
            sessao=sessao,
            aluno_id=aluno_id,
        ).first()

        if presenca is None:
            raise serializers.ValidationError({
                "aluno": "Este aluno não está inscrito na sessão."
            })

        novo_status = request.data.get("status")
        justificativa = request.data.get("justificativa", "")

        if novo_status not in (
            StatusPresenca.PRESENTE,
            StatusPresenca.AUSENTE,
            StatusPresenca.JUSTIFICADO,
        ):
            raise serializers.ValidationError({
                "status": "Informe PRESENTE, AUSENTE ou JUSTIFICADO."
            })

        if not isinstance(justificativa, str):
            raise serializers.ValidationError({
                "justificativa": "A justificativa deve ser um texto."
            })

        try:
            presenca.registrarPresenca(novo_status, justificativa)
        except DjangoValidationError as erro:
            raise serializers.ValidationError({
                "erro": erro.message_dict
                if hasattr(erro, "message_dict")
                else erro.messages
            })

        return Response({
            "mensagem": "Presença registrada com sucesso.",
            "sessao": sessao.pk,
            "aluno": presenca.aluno_id,
            "status": presenca.status,
            "justificativa": presenca.justificativa,
        })

    @action(detail=True, methods=["get"], url_path="presencas")
    def listar_presencas(self, request, pk=None):
        """Lista os alunos inscritos e suas presenças na sessão."""
        sessao = self.get_object()
        usuario = request.user

        administrador = Administrador.objects.filter(pk=usuario.pk).exists()
        treinador = (
            Profissional.objects.filter(pk=usuario.pk).exists()
            and sessao.profissional_id == usuario.pk
        )

        if not administrador and not treinador:
            raise PermissionDenied(
                "Apenas o profissional responsável ou um administrador "
                "pode consultar a lista de presença."
            )

        presencas = Presenca.objects.filter(
            sessao=sessao
        ).select_related("aluno").order_by("aluno__first_name")

        return Response([
            {
                "aluno_id": p.aluno_id,
                "nome": f"{p.aluno.first_name} {p.aluno.last_name}".strip(),
                "status": p.status,
                "justificativa": p.justificativa,
            }
            for p in presencas
        ])


    @action(detail=True, methods=["post"])
    def realizar(self, request, pk=None):
        """Marca como realizada uma sessão confirmada."""
        sessao = self.get_object()

        if not (
            Profissional.objects.filter(pk=request.user.pk).exists()
            and sessao.profissional_id == request.user.pk
        ):
            raise PermissionDenied(
                "Apenas o profissional responsável pode concluir a sessão."
            )

        if sessao.status != StatusSessao.CONFIRMADA:
            raise serializers.ValidationError({
                "status": "A sessão precisa estar confirmada."
            })

        sessao.status = StatusSessao.REALIZADA
        sessao.save(update_fields=["status"])

        return Response(SessaoSerializer(sessao).data)