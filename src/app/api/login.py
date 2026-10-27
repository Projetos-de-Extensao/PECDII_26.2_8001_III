
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"erro": "Informe usuário e senha."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    usuario = authenticate(
        request,
        username=username,
        password=password,
    )

    if usuario is None:
        return Response(
            {"erro": "Usuário ou senha inválidos."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token, _ = Token.objects.get_or_create(user=usuario)

    perfil = getattr(usuario, "perfil_pkz", None)

    return Response({
        "token": token.key,
        "usuario": {
            "id": usuario.id,
            "username": usuario.username,
            "nome": perfil.nome_completo if perfil else usuario.get_full_name(),
            "perfil": perfil.perfil if perfil else None,
        },
    })
