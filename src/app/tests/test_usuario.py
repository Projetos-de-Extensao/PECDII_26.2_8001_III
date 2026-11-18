from datetime import date

from django.test import TestCase
from django.urls import reverse

from app.models import Usuario


class UsuarioTests(TestCase):
    def test_cria_usuario_com_dados_do_diagrama(self):
        usuario = Usuario.objects.create_user(
            username="maria",
            password="senha-segura",
            telefone="11999999999",
            dataNascimento=date(2000, 1, 2),
            endereco="Rua A, 10",
        )

        self.assertEqual(usuario.telefone, "11999999999")
        self.assertEqual(usuario.dataNascimento, date(2000, 1, 2))
        self.assertEqual(usuario.endereco, "Rua A, 10")
        self.assertTrue(usuario.check_password("senha-segura"))

    def test_senha_pode_ser_atualizada_pelo_contrato_do_usuario(self):
        usuario = Usuario.objects.create_user(
            username="joao", password="senha-antiga"
        )

        usuario.set_password("senha-nova")
        usuario.save()

        self.assertTrue(usuario.check_password("senha-nova"))
        self.assertFalse(usuario.check_password("senha-antiga"))

    def test_usuario_campos_unicos_devem_ser_unicos(self):
        Usuario.objects.create_user(
            username="maria", email="maria@example.com", password="senha-segura", telefone="11999999999"
        )

        # same username
        with self.assertRaises(Exception):
            Usuario.objects.create_user(
                username="maria", email="maria2@example.com", password="outra-senha", telefone="11988888888"
            )

        # same email
        with self.assertRaises(Exception):
            Usuario.objects.create_user(
                username="ana", email="maria@example.com", password="outra-senha", telefone="11977777777"
            )

    def test_usuario_criado_pelo_admin_tem_senha_valida(self):
        admin = Usuario.objects.create_superuser(
            username="admin", email="admin@example.com", password="senha-admin"
        )
        self.client.force_login(admin)

        self.client.post(
            reverse("admin:app_usuario_add"),
            {
                "username": "usuario-admin",
                "email": "usuario@example.com",
                "first_name": "Usuario",
                "last_name": "Admin",
                "password1": "senha-segura-123",
                "password2": "senha-segura-123",
                "_save": "Salvar",
            },
        )

        usuario = Usuario.objects.get(username="usuario-admin")
        self.assertTrue(usuario.check_password("senha-segura-123"))
