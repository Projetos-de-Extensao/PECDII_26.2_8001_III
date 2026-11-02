from rest_framework.permissions import BasePermission

from app.models import Administrador


class IsAdministrador(BasePermission):
    """
    Permite acesso somente a administradores autenticados.

    A permissão verifica se o usuário está autenticado,
    se sua conta está ativa e se possui um registro
    correspondente no modelo Administrador.

    Impede que usuários comuns executem operações
    administrativas do sistema PKZ Lab.
    """

    message = "Acesso permitido apenas para administradores."

    def has_permission(self, request, view):
        """
        Verifica se o usuário possui autorização administrativa.

        Args:
            request: Requisição HTTP recebida pela API.
            view: View responsável pela operação solicitada.

        Returns:
            bool: True quando o usuário é um administrador
            autenticado e ativo; False caso contrário.
        """

        # Impede o acesso de usuários não autenticados.
        if not request.user.is_authenticated:
            return False

        # Impede operações realizadas por contas desativadas.
        if not request.user.is_active:
            return False

        # Verifica se existe um Administrador associado ao usuário.
        return Administrador.objects.filter(
            pk=request.user.pk
        ).exists()