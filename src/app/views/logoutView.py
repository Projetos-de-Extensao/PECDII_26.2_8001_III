
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from app.serializers.apiResponseSerializer import DetailResponseSerializer


class LogoutView(APIView):
    """Invalida o token de autenticação do usuário."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: DetailResponseSerializer},
    )
    def post(self, request):
        """Remove o token utilizado na requisição."""
        request.auth.delete()

        return Response({"detail": "Logout realizado com sucesso."})
