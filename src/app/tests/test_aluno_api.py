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

    def test_administrador_cadastra_aluno(self):
        """Administrador cadastra aluno com senha protegida."""
        self.client.force_authenticate(user=self.admin)

        resposta = self.client.post(
            reverse("aluno-list"),
            {
                "username": "novo_aluno",
                "password": "SenhaForte123!",
            },
        )

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)

        aluno = Aluno.objects.get(username="novo_aluno")
        self.assertEqual(aluno.matricula, f"MAT-{aluno.pk:06d}")
        self.assertEqual(resposta.data["matricula"], aluno.matricula)
        self.assertTrue(aluno.check_password("SenhaForte123!"))
        self.assertNotIn("password", resposta.data)


    def test_responsavel_nao_cadastra_aluno(self):
        """Responsável não possui permissão para cadastrar alunos."""
        self.client.force_authenticate(user=self.responsavel)

        resposta = self.client.post(
            reverse("aluno-list"),
            {
                "username": "aluno_indevido",
                "password": "SenhaForte123!",
                "matricula": "MAT-004",
            },
        )

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Aluno.objects.filter(matricula="MAT-004").exists())


    def test_administrador_edita_aluno(self):
        """Administrador edita dados sem alterar a matrícula."""
        self.client.force_authenticate(user=self.admin)
        matricula_original = self.aluno.matricula

        resposta = self.client.patch(
            reverse("aluno-detail", args=[self.aluno.pk]),
            {"first_name": "Carlos", "matricula": "MAT-100"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.first_name, "Carlos")
        self.assertEqual(self.aluno.matricula, matricula_original)


    def test_responsavel_edita_dependente(self):
        """Responsável pode atualizar dados cadastrais do dependente."""
        self.client.force_authenticate(user=self.responsavel)

        resposta = self.client.patch(
            reverse("aluno-detail", args=[self.aluno.pk]),
            {"first_name": "Pedro", "telefone": "21999999999"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.first_name, "Pedro")
        self.assertEqual(self.aluno.telefone, "21999999999")


    def test_responsavel_nao_edita_outro_aluno(self):
        """Responsável não pode editar aluno sem vínculo."""
        self.client.force_authenticate(user=self.responsavel)

        resposta = self.client.patch(
            reverse("aluno-detail", args=[self.outro_aluno.pk]),
            {"first_name": "Alterado"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)


    def test_aluno_nao_edita_proprio_cadastro(self):
        """Aluno possui acesso somente de leitura."""
        self.client.force_authenticate(user=self.aluno)

        resposta = self.client.patch(
            reverse("aluno-detail", args=[self.aluno.pk]),
            {"first_name": "Alterado"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)


    def test_responsavel_nao_altera_campos_restritos(self):
        """Responsável não pode alterar matrícula, créditos ou senha."""
        self.client.force_authenticate(user=self.responsavel)

        resposta = self.client.patch(
            reverse("aluno-detail", args=[self.aluno.pk]),
            {
                "matricula": "MAT-999",
                "creditos": 999,
                "password": "NovaSenha123!",
            },
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)

        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.matricula, "MAT-001")
        self.assertNotEqual(self.aluno.creditos, 999)
        self.assertTrue(self.aluno.check_password("Senha123!"))