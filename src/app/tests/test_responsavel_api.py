
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from app.Enums import StatusSessao
from app.models import Aluno, Presenca, Profissional, Responsavel, Sala, Sessao
from app.models.responsavelModel import VinculoResponsavel


class TestesResponsavelAPI(APITestCase):
    """Verifica inscrições e permissões pela API."""

    def setUp(self):
        """Cria responsáveis, dependente e sessão confirmada."""
        self.responsavel = Responsavel.objects.create_user(
            username="responsavel_api", password="Senha123!"
        )
        self.outro = Responsavel.objects.create_user(
            username="outro_api", password="Senha123!"
        )
        self.aluno = Aluno.objects.create_user(
            username="aluno_api", password="Senha123!",
            matricula="MAT-API-001", creditos=5,
        )
        VinculoResponsavel.objects.create(
            responsavel=self.responsavel, aluno=self.aluno
        )
        sala = Sala.objects.create(numero=102, capacidade=10)
        profissional = Profissional.objects.create_user(
            username="profissional_api", password="Senha123!",
            tipoContrato="CLT", formacao="Educação Física",
        )
        self.sessao = Sessao.objects.create(
            sala=sala,
            profissional=profissional,
            dataHora=timezone.now() + timedelta(days=1),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
            status=StatusSessao.CONFIRMADA,
        )
        self.url_inscricao = reverse(
            "responsavel-inscrever-dependente",
            args=[self.responsavel.pk],
        )
        self.url_cancelamento = reverse(
            "responsavel-cancelar-inscricao",
            args=[self.responsavel.pk],
        )
        self.dados = {
            "aluno_id": self.aluno.pk,
            "sessao_id": self.sessao.pk,
        }

    def test_inscricao_valida(self):
        """Responsável pode inscrever seu dependente."""
        self.client.force_authenticate(user=self.responsavel)
        resposta = self.client.post(self.url_inscricao, self.dados)

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Presenca.objects.filter(
            aluno=self.aluno, sessao=self.sessao
        ).exists())

    def test_inscricao_sem_autenticacao(self):
        """Usuário anônimo não pode inscrever dependentes."""
        resposta = self.client.post(self.url_inscricao, self.dados)
        self.assertIn(resposta.status_code, [401, 403])

    def test_responsavel_nao_acessa_outro_cadastro(self):
        """Responsável não pode agendar pelo cadastro de outra família."""
        self.client.force_authenticate(user=self.outro)
        resposta = self.client.post(self.url_inscricao, self.dados)

        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_inscricao_duplicada(self):
        """API rejeita a segunda inscrição do mesmo aluno."""
        self.client.force_authenticate(user=self.responsavel)
        self.client.post(self.url_inscricao, self.dados)
        resposta = self.client.post(self.url_inscricao, self.dados)

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Presenca.objects.filter(
            aluno=self.aluno, sessao=self.sessao
        ).count(), 1)

    def test_cancelamento_valido(self):
        """Responsável pode cancelar a inscrição do dependente."""
        self.client.force_authenticate(user=self.responsavel)
        self.client.post(self.url_inscricao, self.dados)

        resposta = self.client.delete(
            self.url_cancelamento,
            {**self.dados, "motivo": "Solicitação do responsável"},
            format="json",
        )

        self.assertEqual(resposta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Presenca.objects.filter(
            aluno=self.aluno, sessao=self.sessao
        ).exists())

    def test_cancelamento_sem_motivo(self):
        """Cancelamento sem justificativa deve ser recusado."""
        self.client.force_authenticate(user=self.responsavel)
        self.client.post(self.url_inscricao, self.dados)

        resposta = self.client.delete(
            self.url_cancelamento, self.dados, format="json"
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Presenca.objects.filter(
            aluno=self.aluno, sessao=self.sessao
        ).exists())
