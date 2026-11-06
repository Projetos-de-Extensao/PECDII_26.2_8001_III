from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import Administrador, Aluno, Responsavel
from app.models.responsavelModel import VinculoResponsavel


class TestesAlunoAPI(APITestCase):
    """Verifica as permissões de consulta dos alunos."""

    def setUp(self):
        self.admin = Administrador.objects.create_user(
            username="admin_aluno", password="Senha123!"
        )
        self.responsavel = Responsavel.objects.create_user(
            username="responsavel_aluno", password="Senha123!"
        )
        self.aluno = Aluno.objects.create_user(
            username="aluno_teste", password="Senha123!",
            matricula="MAT-001",
        )
        self.outro_aluno = Aluno.objects.create_user(
            username="outro_aluno", password="Senha123!",
            matricula="MAT-002",
        )
        VinculoResponsavel.objects.create(
            responsavel=self.responsavel,
            aluno=self.aluno,
        )

    def test_administrador_lista_todos(self):
        """Administrador consulta todos os alunos."""
        self.client.force_authenticate(user=self.admin)
        resposta = self.client.get(reverse("aluno-list"))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data), 2)

    def test_responsavel_consulta_apenas_dependente(self):
        """Responsável não visualiza alunos de outras famílias."""
        self.client.force_authenticate(user=self.responsavel)

        resposta = self.client.get(reverse("aluno-list"))
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data), 1)

        resposta = self.client.get(
            reverse("aluno-detail", args=[self.outro_aluno.pk])
        )
        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_aluno_consulta_apenas_proprio_cadastro(self):
        """Aluno não consulta os dados de outro aluno."""
        self.client.force_authenticate(user=self.aluno)

        resposta = self.client.get(
            reverse("aluno-detail", args=[self.aluno.pk])
        )
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)

        resposta = self.client.get(
            reverse("aluno-detail", args=[self.outro_aluno.pk])
        )
        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_sem_autenticacao(self):
        """Usuário anônimo não consulta alunos."""
        resposta = self.client.get(reverse("aluno-list"))
        self.assertIn(resposta.status_code, [401, 403])