
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from app.models import Responsavel
from app.serializers import ResponsavelSerializer
from app.permissions.administradorPermission import IsAdministrador


from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from app.models import Aluno



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
        """Restringe listagens e alterações a administradores."""
        if self.action == "retrieve":
            return [IsAuthenticated()]

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

