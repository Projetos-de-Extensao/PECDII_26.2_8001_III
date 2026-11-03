
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from app.models import Responsavel
from app.serializers import ResponsavelSerializer
from app.permissions.administradorPermission import IsAdministrador


class ResponsavelView(ModelViewSet):
    """Disponibiliza o cadastro e a consulta de responsáveis."""

    queryset = Responsavel.objects.all()
    serializer_class = ResponsavelSerializer

    def get_permissions(self):
        """Restringe alterações a administradores."""
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]

        return [IsAdministrador()]
