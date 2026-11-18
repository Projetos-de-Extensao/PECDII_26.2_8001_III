from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from app.models import Administrador, Responsavel, Profissional
from app.serializers.usuarioSerializer import MeResponseSerializer


class MeView(APIView):
    """Retorna o perfil do usuário autenticado."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: MeResponseSerializer})
    def get(self, request):
        usuario = request.user

        if Administrador.objects.filter(pk=usuario.pk).exists():
            perfil = "administrador"
        elif Responsavel.objects.filter(pk=usuario.pk).exists():
            perfil = "responsavel"
        elif Profissional.objects.filter(pk=usuario.pk).exists():
            perfil = "profissional"
        else:
            perfil = "usuario"

        return Response({
            "id": usuario.pk,
            "username": usuario.username,
            "nome": usuario.get_full_name() or usuario.username,
            "perfil": perfil,
        })