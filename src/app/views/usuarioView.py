from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions

from app.models import Usuario
from app.serializers import UsuarioSerializer

class UsuarioView(ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    # Permite acesso a qualquer usuário, para fins de teste. Em produção, deve-se restringir o acesso a usuários autenticados.
    permission_classes = [permissions.AllowAny]