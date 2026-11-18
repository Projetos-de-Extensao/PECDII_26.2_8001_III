from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import (
    Administrador,
    Treinador,
    Fisioterapeuta,
    Psicologo,
    Nutricionista,
    Usuario,
)


class TestesProfissionalAPI(APITestCase):
    """Valida consultas e filtros de profissionais."""

    def setUp(self):
        self.profissionais = {
            "treinador": Treinador.objects.create(
                username="treinador_api",
                email="treinador@example.test",
                telefone="555-0101",
                tipoContrato="CLT",
                formacao="Educacao Fisica",
                especialidade="Futebol",
            ),
            "fisioterapeuta": Fisioterapeuta.objects.create(
                username="fisio_api",
                tipoContrato="PJ",
                formacao="Fisioterapia",
                CREFITO="12345",
            ),
            "psicologo": Psicologo.objects.create(
                username="psico_api",
                tipoContrato="PJ",
                formacao="Psicologia",
                CRP="54321",
            ),
            "nutricionista": Nutricionista.objects.create(
                username="nutri_api",
                tipoContrato="CLT",
                formacao="Nutricao",
                CRN="98765",
            ),
        }

        self.client.force_authenticate(
            user=self.profissionais["treinador"]
        )

    def test_lista_profissionais(self):
        """Lista os quatro profissionais cadastrados."""
        resposta = self.client.get(reverse("profissional-list"))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data), 4)

    def test_identifica_especializacoes(self):
        """Retorna a especialização correta de cada profissional."""
        for tipo, profissional in self.profissionais.items():
            with self.subTest(tipo=tipo):
                resposta = self.client.get(
                    reverse("profissional-detail", args=[profissional.pk])
                )

                self.assertEqual(resposta.status_code, status.HTTP_200_OK)
                self.assertEqual(resposta.data["tipo"], tipo)
                self.assertNotIn("password", resposta.data)
                self.assertNotIn("email", resposta.data)
                self.assertNotIn("telefone", resposta.data)
                self.assertNotIn("dataNascimento", resposta.data)
                self.assertNotIn("endereco", resposta.data)

    def test_filtros_por_especializacao(self):
        """Cada filtro retorna somente a especialização solicitada."""
        for tipo, profissional in self.profissionais.items():
            with self.subTest(tipo=tipo):
                resposta = self.client.get(
                    reverse("profissional-list"), {"tipo": tipo}
                )

                self.assertEqual(resposta.status_code, status.HTTP_200_OK)
                self.assertEqual(len(resposta.data), 1)
                self.assertEqual(resposta.data[0]["id"], profissional.pk)

    def test_tipo_invalido(self):
        """Rejeita especialização inexistente."""
        resposta = self.client.get(
            reverse("profissional-list"), {"tipo": "invalido"}
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sem_autenticacao(self):
        """Bloqueia consultas sem autenticação."""
        self.client.force_authenticate(user=None)
        resposta = self.client.get(reverse("profissional-list"))

        self.assertIn(resposta.status_code, [401, 403])

    def test_usuario_generico_nao_consulta_profissionais(self):
        usuario = Usuario.objects.create_user(
            username="usuario_generico_profissionais",
            password="Senha123!",
        )
        self.client.force_authenticate(user=usuario)

        resposta_lista = self.client.get(reverse("profissional-list"))
        resposta_detalhe = self.client.get(
            reverse(
                "profissional-detail",
                args=[self.profissionais["treinador"].pk],
            )
        )

        self.assertEqual(resposta_lista.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta_lista.data, [])
        self.assertEqual(
            resposta_detalhe.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_administrador_consulta_campos_administrativos_de_profissionais(self):
        administrador = Administrador.objects.create_user(
            username="admin_profissionais",
            password="Senha123!",
            tipoContrato="CLT",
        )
        self.client.force_authenticate(user=administrador)

        resposta = self.client.get(
            reverse(
                "profissional-detail",
                args=[self.profissionais["treinador"].pk],
            )
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data["email"], "treinador@example.test")
        self.assertEqual(resposta.data["telefone"], "555-0101")
        self.assertEqual(resposta.data["tipoContrato"], "CLT")