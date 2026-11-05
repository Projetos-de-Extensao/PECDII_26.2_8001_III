"""Testes de autenticação por token e autorização da API do PKZ Lab."""

from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from app.models import Administrador, Responsavel, Usuario


class TestesAutenticacao(TestCase):
    """Valida login, logout e proteção dos endpoints por perfil."""

    def setUp(self):
        """Cria contas isoladas no banco temporário de testes."""
        self.admin = Administrador.objects.create_user(
            username="admin_autenticacao", password="SenhaSegura123!", tipoContrato="CLT"
        )
        self.comum = Usuario.objects.create_user(
            username="comum_autenticacao", password="SenhaSegura123!"
        )
        self.responsavel = Responsavel.objects.create_user(
            username="responsavel_autenticacao", password="SenhaSegura123!"
        )
        self.cliente = APIClient()
        self.url_login = reverse("login")
        self.url_logout = reverse("logout")
        self.url_usuarios = reverse("usuario-list")
        self.url_responsaveis = reverse("responsavel-list")

    def autenticar_token(self, usuario):
        """Configura o cabeçalho Authorization com um token real."""
        token, _ = Token.objects.get_or_create(user=usuario)
        self.cliente.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        return token

    def test_login_valido_retorna_token(self):
        """Credenciais corretas geram um token associado ao usuário."""
        resposta = self.cliente.post(
            self.url_login,
            {"username": self.admin.username, "password": "SenhaSegura123!"},
            format="json",
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["usuario_id"], self.admin.pk)
        self.assertEqual(resposta.data["token"], Token.objects.get(user=self.admin).key)

    def test_login_senha_incorreta(self):
        """Uma senha inválida não autentica o usuário."""
        resposta = self.cliente.post(
            self.url_login,
            {"username": self.admin.username, "password": "incorreta"},
            format="json",
        )
        self.assertEqual(resposta.status_code, 401)
        self.assertFalse(Token.objects.filter(user=self.admin).exists())

    def test_login_sem_credenciais(self):
        """Login exige usuário e senha."""
        resposta = self.cliente.post(self.url_login, {"username": self.admin.username}, format="json")
        self.assertEqual(resposta.status_code, 400)

    def test_usuario_inativo_nao_faz_login(self):
        """Contas desativadas não recebem tokens."""
        self.comum.is_active = False
        self.comum.save(update_fields=["is_active"])
        resposta = self.cliente.post(
            self.url_login,
            {"username": self.comum.username, "password": "SenhaSegura123!"},
            format="json",
        )
        self.assertEqual(resposta.status_code, 401)
        self.assertFalse(Token.objects.filter(user=self.comum).exists())

    def test_endpoint_protegido_sem_token(self):
        """Requisições anônimas não acessam usuários cadastrados."""
        resposta = self.cliente.get(self.url_usuarios)
        self.assertEqual(resposta.status_code, 401)

    def test_token_valido_permite_acesso_administrativo(self):
        """O administrador autenticado pode listar usuários."""
        self.autenticar_token(self.admin)
        resposta = self.cliente.get(self.url_usuarios)
        self.assertEqual(resposta.status_code, 200)

    def test_logout_invalida_token(self):
        """O token deixa de autenticar após o logout."""
        token = self.autenticar_token(self.admin)
        self.assertEqual(self.cliente.get(self.url_usuarios).status_code, 200)
        self.assertEqual(self.cliente.post(self.url_logout).status_code, 200)
        self.assertFalse(Token.objects.filter(pk=token.pk).exists())
        self.assertEqual(self.cliente.get(self.url_usuarios).status_code, 401)

    def test_logout_sem_token(self):
        """Usuários anônimos não podem realizar logout."""
        resposta = self.cliente.post(self.url_logout)