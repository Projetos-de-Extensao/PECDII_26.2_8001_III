from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from app.models import Usuario
from app.serializers import UsuarioSerializer
from app.permissions.administradorPermission import IsAdministrador


class UsuarioView(ModelViewSet):
    """
    Disponibiliza operações de consulta e gerenciamento
    dos usuários cadastrados no PKZ Lab.

    Operações de escrita são restritas a administradores.

    A criação de usuários deve utilizar preferencialmente
    o endpoint administrativo, que executa o método
    Administrador.cadastrarUsuario().
    """

    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        """Restringe a consulta aos próprios dados ou aos administradores."""
        usuario = self.request.user

        if IsAdministrador().has_permission(self.request, self):
            return Usuario.objects.all()

        return Usuario.objects.filter(pk=usuario.pk)


    def get_permissions(self):
        """
        Define as permissões conforme a operação solicitada.

        Consultas exigem autenticação.
        Operações de escrita exigem autorização administrativa.
        """

        # Consulta individual exige autenticação.
        if self.action == "retrieve":
            return [IsAuthenticated()]

        # Cadastro, atualização e exclusão.
        return [IsAdministrador()]