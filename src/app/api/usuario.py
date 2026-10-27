from rest_framework import viewsets

from app.models.usuario import Usuario
from app.serializers.usuario import UsuarioSerializer
from app.permissions.usuario import PermissaoUsuario


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [PermissaoUsuario]