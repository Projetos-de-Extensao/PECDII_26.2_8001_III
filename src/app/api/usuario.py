from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import action

from app.models.usuario import Usuario
from app.serializers.usuario import UsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer