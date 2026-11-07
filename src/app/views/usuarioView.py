from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from app.models import Usuario
from app.serializers import UsuarioSerializer
from app.permissions.administradorPermission import IsAdministrador


class UsuarioView(ModelViewSet):
    """
    Disponibiliza operações de consulta e gerenciamento
    dos usuários cadastrados no PKZ Lab.

    Operações de escrita são restritas a administradores.

    A criação de usuários deve utilizar preferencialmente
    o endpoint administrativo, que executa o método
    Administrador.cadastrarUsuario().
    """

    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        """Restringe a consulta aos próprios dados ou aos administradores."""
        usuario = self.request.user

        if IsAdministrador().has_permission(self.request, self):
            return Usuario.objects.all()

        return Usuario.objects.filter(pk=usuario.pk)


    def get_permissions(self):
        """
        Define as permissões conforme a operação solicitada.

        Consultas exigem autenticação.
        Operações de escrita exigem autorização administrativa.
        """

        if self.action == "ativar_conta":
            return [AllowAny()]
        
        if self.action == "alterar_senha":
            return [IsAuthenticated()]

        # Consulta individual exige autenticação.
        if self.action == "retrieve":
            return [IsAuthenticated()]

        # Cadastro, atualização e exclusão.
        return [IsAdministrador()]

    @action(detail=False, methods=["post"], url_path="alterar-senha")
    def alterar_senha(self, request):
        """Permite ao usuário autenticado alterar a própria senha."""
        usuario = request.user
        senha_atual = request.data.get("senha_atual")
        nova_senha = request.data.get("nova_senha")

        if not senha_atual or not nova_senha:
            return Response(
                {"erro": "Informe a senha atual e a nova senha."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not usuario.check_password(senha_atual):
            return Response(
                {"erro": "Senha atual incorreta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(nova_senha, user=usuario)
        except ValidationError as erro:
            return Response(
                {"erro": erro.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario.set_password(nova_senha)
        usuario.save(update_fields=["password"])

        return Response(
            {"mensagem": "Senha alterada com sucesso."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="ativar-conta",
        permission_classes=[AllowAny],
        authentication_classes=[],
    )
    def ativar_conta(self, request):
        """Permite definir a senha usando um convite válido."""
        uid = request.data.get("uid")
        token = request.data.get("token")
        nova_senha = request.data.get("nova_senha")

        if not all([uid, token, nova_senha]):
            return Response(
                {"erro": "Informe uid, token e nova senha."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            usuario_id = force_str(urlsafe_base64_decode(uid))
            usuario = Usuario.objects.get(pk=usuario_id)
        except (ValueError, TypeError, OverflowError, Usuario.DoesNotExist):
            return Response(
                {"erro": "Convite inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if usuario.has_usable_password() or not default_token_generator.check_token(usuario, token):
            return Response(
                {"erro": "Convite inválido ou expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(nova_senha, user=usuario)
        except ValidationError as erro:
            return Response(
                {"erro": erro.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario.set_password(nova_senha)
        usuario.save(update_fields=["password"])

        return Response(
            {"mensagem": "Conta ativada com sucesso."},
            status=status.HTTP_200_OK,
        )