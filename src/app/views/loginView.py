
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from app.models import Aluno
from app.serializers.loginSerializer import LoginSerializer

class LoginView(APIView):
    """Autentica usuários e fornece um token de acesso."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=LoginSerializer,
        description="Autentica o usuário e retorna um token.",
    )
    def post(self, request):
        """Valida as credenciais e retorna o token."""
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Informe usuário e senha."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario = authenticate(
            request,
            username=username,
            password=password,
        )

        if usuario is None or not usuario.is_active:
            return Response(
                {"detail": "Credenciais inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Alunos não possuem acesso individual à plataforma.
        if Aluno.objects.filter(pk=usuario.pk).exists():
            return Response(
                {"detail": "Credenciais inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=usuario)

        return Response({
            "token": token.key,
            "usuario_id": usuario.pk,
            "username": usuario.username,
        })
