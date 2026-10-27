
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from app.models.usuario import Usuario


class TestesAutenticacao(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Administrador da PKZ Lab
        self.admin = User.objects.create_user(
            username="admin_teste",
            password="teste1234"
        )

        Usuario.objects.create(
            conta=self.admin,
            nome_completo="Administrador Teste",
            nome_usuario="admin_teste",
            perfil="administrador"
        )

        # Recepção
        self.recepcao = User.objects.create_user(
            username="recepcao_teste",
            password="teste1234"
        )

        Usuario.objects.create(
            conta=self.recepcao,
            nome_completo="Recepcao Teste",
            nome_usuario="recepcao_teste",
            perfil="recepcao"
        )

        # Professor PKZ
        self.professor = User.objects.create_user(
            username="professor_teste",
            password="teste1234"
        )

        Usuario.objects.create(
            conta=self.professor,
            nome_completo="Professor Teste",
            nome_usuario="professor_teste",
            perfil="professor_pkz"
        )

    def test_login_correto(self):
        resposta = self.client.post(
            "/api/login/",
            {
                "username": "professor_teste",
                "password": "teste1234"
            },
            format="json"
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("token", resposta.data)
        self.assertEqual(
            resposta.data["usuario"]["perfil"],
            "professor_pkz"
        )

    def test_login_senha_incorreta(self):
        resposta = self.client.post(
            "/api/login/",
            {
                "username": "professor_teste",
                "password": "senha_errada"
            },
            format="json"
        )

        self.assertEqual(resposta.status_code, 401)

    def test_login_sem_credenciais(self):
        resposta = self.client.post(
            "/api/login/",
            {},
            format="json"
        )

        self.assertEqual(resposta.status_code, 400)

    def test_cadastro_usuario_administrador(self):
        self.client.force_authenticate(user=self.admin)

        resposta = self.client.post(
            "/api/usuarios/",
            {
                "nome_completo": "Novo Responsavel",
                "nome_usuario": "novo_responsavel",
                "perfil": "responsavel",
                "senha": "teste1234"
            },
            format="json"
        )

        self.assertEqual(resposta.status_code, 201)
        self.assertNotIn("senha", resposta.data)

        conta = User.objects.get(username="novo_responsavel")
        self.assertTrue(
            conta.check_password("teste1234")
        )
        self.assertEqual(
            conta.perfil_pkz.perfil,
            "responsavel"
        )

    def test_professor_nao_pode_gerenciar_usuarios(self):
        self.client.force_authenticate(user=self.professor)

        resposta = self.client.get("/api/usuarios/")

        self.assertEqual(resposta.status_code, 403)

    def test_recepcao_nao_pode_gerenciar_usuarios(self):
        self.client.force_authenticate(user=self.recepcao)

        resposta = self.client.get("/api/usuarios/")

        self.assertEqual(resposta.status_code, 403)

    def test_administrador_pode_gerenciar_usuarios(self):
        self.client.force_authenticate(user=self.admin)

        resposta = self.client.get("/api/usuarios/")

        self.assertEqual(resposta.status_code, 200)

    def test_professor_nao_pode_acessar_alunos(self):
        self.client.force_authenticate(user=self.professor)

        resposta = self.client.get("/api/alunos/")

        self.assertEqual(resposta.status_code, 403)

    def test_recepcao_pode_acessar_alunos(self):
        self.client.force_authenticate(user=self.recepcao)

        resposta = self.client.get("/api/alunos/")

        self.assertEqual(resposta.status_code, 200)

    def test_logout_invalida_token(self):
        token = Token.objects.create(user=self.professor)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        resposta = self.client.post("/api/logout/")

        self.assertEqual(resposta.status_code, 200)

        self.assertFalse(
            Token.objects.filter(key=token.key).exists()
        )

        resposta = self.client.get("/api/usuarios/")

        self.assertEqual(resposta.status_code, 401)
