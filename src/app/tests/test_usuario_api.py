from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from app.models import Usuario, Administrador


class UsuarioAPITests(TestCase):
    """
    Testes das permissões e operações da API de usuários.
    """

    def setUp(self):
        """
        Prepara um administrador, um usuário comum
        e um cliente para realizar requisições HTTP.
        """

        self.administrador = Administrador.objects.create_user(
            username="admin_usuario_api",
            password="senha123",
            tipoContrato="CLT"
        )

        self.usuario = Usuario.objects.create_user(
            username="usuario_teste",
            password="senha123"
        )

        self.client = APIClient()

    def test_usuario_comum_nao_cadastra_conta(self):
        """
        Verifica se um usuário comum não pode
        cadastrar outros usuários.
        """

        self.client.force_authenticate(user=self.usuario)

        url = reverse("usuario-list")

        resposta = self.client.post(
            url,
            {
                "username": "conta_indevida",
                "password": "senhaSegura123"
            },
            format="json"
        )

        self.assertEqual(resposta.status_code, 403)

        self.assertFalse(
            Usuario.objects.filter(
                username="conta_indevida"
            ).exists()
        )

    def test_usuario_comum_nao_exclui_conta(self):
        """
        Verifica se um usuário comum não pode
        excluir contas de outros usuários.
        """

        self.client.force_authenticate(user=self.usuario)

        url = reverse(
            "usuario-detail",
            kwargs={"pk": self.administrador.pk}
        )

        resposta = self.client.delete(url)

        self.assertEqual(resposta.status_code, 403)

        self.assertTrue(
            Usuario.objects.filter(
                pk=self.administrador.pk
            ).exists()
        )

    def test_administrador_consulta_usuarios(self):
        """
        Verifica se o administrador consegue
        consultar os usuários cadastrados.
        """

        self.client.force_authenticate(
            user=self.administrador
        )

        url = reverse("usuario-list")

        resposta = self.client.get(url)

        self.assertEqual(resposta.status_code, 200)

    def test_atualizar_usuario_sem_alterar_senha(self):
        """
        Verifica se uma atualização parcial mantém
        a senha original quando nenhuma nova senha
        é informada.
        """

        self.client.force_authenticate(
            user=self.administrador
        )

        url = reverse(
            "usuario-detail",
            kwargs={"pk": self.usuario.pk}
        )

        resposta = self.client.patch(
            url,
            {"first_name": "João"},
            format="json"
        )

        self.assertEqual(resposta.status_code, 200)

        self.usuario.refresh_from_db()

        self.assertEqual(
            self.usuario.first_name,
            "João"
        )

        self.assertTrue(
            self.usuario.check_password("senha123")
        )