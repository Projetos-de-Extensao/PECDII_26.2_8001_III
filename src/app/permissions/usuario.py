from rest_framework.permissions import BasePermission


class PermissaoUsuario(BasePermission):
    message = "Apenas administradores podem gerenciar usuários."

    def has_permission(self, request, view):
        usuario = request.user

        if not usuario.is_authenticated:
            return False

        if usuario.is_superuser:
            return True

        perfil = getattr(usuario, "perfil_pkz", None)

        if perfil is None:
            return False

        return perfil.perfil == "administrador"