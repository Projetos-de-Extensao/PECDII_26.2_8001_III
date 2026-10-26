from rest_framework import viewsets
from rest_framework.permissions import  IsAdminUser

from app.models.usuario import Usuario
from app.serializers.usuario import UsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer