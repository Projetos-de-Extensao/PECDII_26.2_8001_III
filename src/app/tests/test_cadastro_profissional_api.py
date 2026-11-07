from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import (
    Administrador, Usuario, Profissional,
    Treinador, Fisioterapeuta, Psicologo, Nutricionista,
)


class TestesCadastroProfissionalAPI(APITestCase):
    """Valida o cadastro administrativo de profissionais."""

    def setUp(self):
        self.admin = Administrador.objects.create_user(
            username="admin_cadastro",
            password="SenhaTeste123!",
            tipoContrato="CLT",
        )
        self.client.force_authenticate(user=self.admin)
        self.url = reverse("administrador-cadastrar-usuario")

        self.dados = {
            "username": "profissional_teste",
            "password": "SenhaTeste123!",
            "tipoContrato": "CLT",
            "formacao": "Formacao de teste",
        }

    def test_cadastro_especializacoes(self):
        """Cria corretamente as quatro especializações."""
        casos = [
            ("treinador", "especialidade", "Futebol", Treinador),
            ("fisioterapeuta", "CREFITO", "12345", Fisioterapeuta),
            ("psicologo", "CRP", "54321", Psicologo),
            ("nutricionista", "CRN", "98765", Nutricionista),
        ]

        for indice, (tipo, campo, valor, modelo) in enumerate(casos):
            with self.subTest(tipo=tipo):
                dados = {
                    **self.dados,
                    "username": f"profissional_{indice}",
                    "tipo": tipo,
                    campo: valor,
                }

                resposta = self.client.post(self.url, dados)

                self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)

                profissional = modelo.objects.get(username=dados["username"])

                self.assertTrue(
                    profissional.check_password(dados["password"])
                )
                self.assertTrue(
                    Profissional.objects.filter(pk=profissional.pk).exists()
                )

    def test_tipo_invalido(self):
        """Rejeita especializações desconhecidas."""
        resposta = self.client.post(
            self.url,
            {**self.dados, "tipo": "medico"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Usuario.objects.filter(username="profissional_teste").exists()
        )

    def test_campo_especifico_obrigatorio(self):
        """Exige o registro correspondente à especialização."""
        resposta = self.client.post(
            self.url,
            {**self.dados, "tipo": "psicologo"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_usuario_comum_sem_tipo(self):
        """Preserva o cadastro comum existente."""
        resposta = self.client.post(self.url, self.dados)

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Usuario.objects.filter(username="profissional_teste").exists()
        )


    def test_usuario_comum_nao_cadastra_profissional(self):
        """Impede cadastro de profissionais por usuários comuns."""
        usuario = Usuario.objects.create_user(
            username="usuario_comum",
            password="SenhaTeste123!",
        )
        self.client.force_authenticate(user=usuario)

        resposta = self.client.post(
            self.url,
            {
                **self.dados,
                "tipo": "treinador",
                "especialidade": "Futebol",
            },
        )

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            Profissional.objects.filter(
                username="profissional_teste"
            ).exists()
        )