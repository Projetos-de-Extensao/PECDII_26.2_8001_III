from datetime import date

from django.test import TestCase

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
