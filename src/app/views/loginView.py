
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


class LoginView(APIView):
    """Autentica usuários utilizando o sistema do Django."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Valida credenciais e inicia uma sessão autenticada."""
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

        if usuario is None:
            return Response(
                {"detail": "Credenciais inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, usuario)

        return Response(
            {
                "detail": "Login realizado com sucesso.",
                "usuario_id": usuario.pk,
                "username": usuario.username,
            },
            status=status.HTTP_200_OK,
        )
