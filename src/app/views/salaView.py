from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from app.models import Sala
from app.serializers import SalaSerializer
from app.permissions.administradorPermission import IsAdministrador


class SalaView(ModelViewSet):

    """
    Gerencia as operações da API de salas.

    Usuários autenticados podem consultar salas.
    Apenas administradores podem cadastrar,
    atualizar ou excluir salas.
    """
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer

   
    def get_permissions(self):
        """
        Define as permissões conforme a operação.

        Consultas exigem autenticação.
        Alterações exigem autorização administrativa.
        """

        # Permite consultar salas mediante autenticação.
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]

        # Restringe cadastro, edição e exclusão.
        return [IsAdministrador()]
