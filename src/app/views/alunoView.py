from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db.models import Q

from app.models import Aluno
from app.serializers import AlunoSerializer
from app.permissions.administradorPermission import IsAdministrador


class AlunoView(ReadOnlyModelViewSet):
    """Permite consultar alunos conforme o vínculo do usuário."""

    serializer_class = AlunoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Restringe os alunos aos autorizados a consultá-los."""
        usuario = self.request.user

        if IsAdministrador().has_permission(self.request, self):
            return Aluno.objects.all()

        return Aluno.objects.filter(
            Q(pk=usuario.pk) |
            Q(vinculo_responsavel__responsavel_id=usuario.pk)
        )