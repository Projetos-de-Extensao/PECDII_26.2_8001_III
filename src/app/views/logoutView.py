
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class LogoutView(APIView):
    """Invalida o token de autenticação do usuário."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Remove o token utilizado na requisição."""
        request.auth.delete()

        return Response({"detail": "Logout realizado com sucesso."})
