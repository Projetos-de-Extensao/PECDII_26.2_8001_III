
from rest_framework.permissions import BasePermission


class PermissaoAluno(BasePermission):
    message = "Você não tem permissão para acessar alunos."

    def has_permission(self, request, view):
        usuario = request.user

        if not usuario.is_authenticated:
            return False

        # Superusuários possuem acesso completo.
        if usuario.is_superuser:
            return True

        perfil = getattr(usuario, "perfil_pkz", None)

        if perfil is None:
            return False

        # Administradores e recepção podem gerenciar alunos.
        if perfil.perfil in ["administrador", "recepcao"]:
            return True

        return False
