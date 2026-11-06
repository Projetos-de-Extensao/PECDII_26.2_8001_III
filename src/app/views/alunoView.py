from django.db.models import Q
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from app.models import Aluno
from app.serializers import AlunoSerializer
from app.permissions.administradorPermission import IsAdministrador


class AlunoView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """Permite cadastrar e consultar alunos conforme as permissões."""

    serializer_class = AlunoSerializer

    def get_permissions(self):
        """Restringe o cadastro aos administradores."""
        if self.action == "create":
            return [IsAdministrador()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Restringe os alunos aos autorizados a consultá-los."""
        usuario = self.request.user

        if IsAdministrador().has_permission(self.request, self):
            return Aluno.objects.all()

        if self.action == "partial_update":
            return Aluno.objects.filter(
                vinculo_responsavel__responsavel_id=usuario.pk
            )

        return Aluno.objects.filter(
            Q(pk=usuario.pk) |
            Q(vinculo_responsavel__responsavel_id=usuario.pk)
        )

    def update(self, request, *args, **kwargs):
        """Permite somente atualização parcial."""
        if not kwargs.get("partial", False):
            from rest_framework.exceptions import MethodNotAllowed
            raise MethodNotAllowed("PUT")

        return super().update(request, *args, **kwargs)