from rest_framework.permissions import BasePermission

from app.models import Responsavel


class IsResponsavel(BasePermission):
    """Permite acesso somente a responsáveis autenticados e ativos."""

    message = "Acesso permitido apenas para responsáveis."

    def has_permission(self, request, view):
        """Verifica se o usuário possui perfil de responsável."""
        usuario = request.user

        return (
            usuario.is_authenticated
            and usuario.is_active
            and Responsavel.objects.filter(pk=usuario.pk).exists()
        )
