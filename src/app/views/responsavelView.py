from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.models import Aluno, Responsavel, Sessao
from app.serializers import ResponsavelSerializer
from app.permissions.administradorPermission import IsAdministrador
from app.permissions.responsavelPermission import IsResponsavel


class ResponsavelView(ModelViewSet):
    """Disponibiliza o cadastro e a consulta de responsáveis."""

    queryset = Responsavel.objects.all()
    serializer_class = ResponsavelSerializer
    

    def get_queryset(self):
        """Permite consultar todos os responsáveis ou apenas o próprio cadastro."""
        usuario = self.request.user

        if IsAdministrador().has_permission(self.request, self):
            return Responsavel.objects.all()

        return Responsavel.objects.filter(pk=usuario.pk)


    def get_permissions(self):
        """Define o acesso conforme a operação solicitada."""
        if self.action == "retrieve":
            return [IsAuthenticated()]

        if self.action in ["inscrever_dependente", "cancelar_inscricao"]:
            return [IsResponsavel()]

        return [IsAdministrador()]


    
    @action(detail=True, methods=["post"], url_path="dependentes")
    def adicionar_dependente(self, request, pk=None):
        """Vincula um aluno ao responsável."""
        responsavel = self.get_object()
        aluno = get_object_or_404(Aluno, pk=request.data.get("aluno_id"))

        try:
            responsavel.adicionarDependente(aluno)
        except IntegrityError:
            raise ValidationError("Aluno já possui responsável.")

        return Response(
            {"detail": "Dependente adicionado."},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"dependentes/(?P<aluno_id>[^/.]+)",
    )
    def remover_dependente(self, request, pk=None, aluno_id=None):
        """Remove o vínculo de um aluno."""
        responsavel = self.get_object()
        aluno = get_object_or_404(Aluno, pk=aluno_id)

        try:
            responsavel.removerDependente(aluno)
        except DjangoValidationError as erro:
            raise ValidationError(erro.messages)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="transferir")
    def transferir_responsabilidade(self, request, pk=None):
        """Transfere um aluno para outro responsável."""
        responsavel = self.get_object()
        aluno = get_object_or_404(Aluno, pk=request.data.get("aluno_id"))
        novo = get_object_or_404(
            Responsavel,
            pk=request.data.get("novo_responsavel_id"),
        )

        try:
            responsavel.transferirResponsabilidade(aluno, novo)
        except DjangoValidationError as erro:
            raise ValidationError(erro.messages)

        return Response({"detail": "Responsabilidade transferida."})

    @action(detail=True, methods=["post"], url_path="inscricoes")
    def inscrever_dependente(self, request, pk=None):
        """Inscreve um dependente em uma sessão."""
        responsavel = self.get_object()
        aluno = get_object_or_404(Aluno, pk=request.data.get("aluno_id"))
        sessao = get_object_or_404(Sessao, pk=request.data.get("sessao_id"))

        try:
            responsavel.inscreverDependenteEmSessao(aluno, sessao)
        except DjangoValidationError as erro:
            raise ValidationError(erro.messages)

        return Response(
            {"detail": "Dependente inscrito."},
            status=status.HTTP_201_CREATED,
        )


    @action(detail=True, methods=["delete"], url_path="inscricoes/cancelar")
    def cancelar_inscricao(self, request, pk=None):
        """Cancela a inscrição de um dependente em uma sessão."""
        responsavel = self.get_object()
        aluno = get_object_or_404(Aluno, pk=request.data.get("aluno_id"))
        sessao = get_object_or_404(Sessao, pk=request.data.get("sessao_id"))

        try:
            responsavel.cancelarInscricaoDependenteEmSessao(
                aluno, sessao, request.data.get("motivo")
            )
        except DjangoValidationError as erro:
            raise ValidationError(erro.messages)

        return Response(status=status.HTTP_204_NO_CONTENT)

