
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class LogoutView(APIView):
    """Encerra a sessão do usuário autenticado."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Realiza logout e invalida a sessão atual."""
        logout(request)

        return Response(
            {"detail": "Logout realizado com sucesso."},
            status=status.HTTP_200_OK,
        )
