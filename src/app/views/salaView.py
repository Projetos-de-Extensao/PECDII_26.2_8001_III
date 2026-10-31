from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions

from app.models import Sala
from app.serializers import SalaSerializer


class SalaView(ModelViewSet):
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer

    # Permite acesso a qualquer usuário, para fins de teste. Em produção, deve-se restringir o acesso a usuários autenticados.
    permission_classes = [permissions.AllowAny]
