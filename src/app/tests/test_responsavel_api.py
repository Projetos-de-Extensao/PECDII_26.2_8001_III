
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from app.Enums import StatusSessao
from app.models import (
    Administrador,
    Aluno,
    Presenca,
    Profissional,
    Responsavel,
    Sala,
    Sessao,
)
from app.models.responsavelModel import VinculoResponsavel
from app.Enums.StatusPresencaEnum import StatusPresenca


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

    def test_api_rejeita_inscricao_em_sessao_sobreposta(self):
        """API rejeita inscrição em sessão diferente com horário conflitante."""
        outra_sala = Sala.objects.create(numero=103, capacidade=10)
        outra_sessao = Sessao.objects.create(
            sala=outra_sala,
            profissional=self.sessao.profissional,
            dataHora=self.sessao.dataHora + timedelta(minutes=30),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
            status=StatusSessao.CONFIRMADA,
        )
        self.client.force_authenticate(user=self.responsavel)
        primeira = self.client.post(self.url_inscricao, self.dados)
        segunda = self.client.post(
            self.url_inscricao,
            {**self.dados, "sessao_id": outra_sessao.pk},
        )

        self.assertEqual(primeira.status_code, status.HTTP_201_CREATED)
        self.assertEqual(segunda.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("conflitante", str(segunda.data))
        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.creditos, 3)

    def test_api_rejeita_data_de_nascimento_de_responsavel_menor(self):
        """Impede atualizar o responsável para uma idade inferior a 18."""
        administrador = Administrador.objects.create_user(
            username="admin_responsavel_idade",
            password="Senha123!",
            tipoContrato="CLT",
        )
        hoje = timezone.localdate()
        try:
            nascimento_de_18_anos = hoje.replace(year=hoje.year - 18)
        except ValueError:
            nascimento_de_18_anos = hoje.replace(
                year=hoje.year - 18,
                day=28,
            )
        data_menor = nascimento_de_18_anos + timedelta(days=1)
        self.client.force_authenticate(user=administrador)

        resposta = self.client.patch(
            reverse("responsavel-detail", args=[self.responsavel.pk]),
            {"dataNascimento": data_menor.isoformat()},
            format="json",
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.responsavel.refresh_from_db()
        self.assertIsNone(self.responsavel.dataNascimento)

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
        presenca = Presenca.objects.get(aluno=self.aluno, sessao=self.sessao)
        self.assertEqual(presenca.status, StatusPresenca.DESISTENTE)

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

    
    def test_inscricao_desconta_creditos(self):
        """Desconta os créditos somente após inscrição válida."""
        self.client.force_authenticate(user=self.responsavel)

        resposta = self.client.post(self.url_inscricao, self.dados)
        self.aluno.refresh_from_db()

        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(self.aluno.creditos, 3)

    def test_cancelamento_antecipado_devolve_creditos(self):
        """Devolve créditos quando faltam pelo menos 12 horas."""
        self.client.force_authenticate(user=self.responsavel)
        self.client.post(self.url_inscricao, self.dados)

        resposta = self.client.delete(
            self.url_cancelamento,
            {**self.dados, "motivo": "Desistência"},
            format="json",
        )
        self.aluno.refresh_from_db()

        self.assertEqual(resposta.status_code, 204)
        self.assertEqual(self.aluno.creditos, 5)

    def test_cancelamento_tardio_nao_devolve_creditos(self):
        """Não reembolsa cancelamentos com menos de 12 horas."""
        self.client.force_authenticate(user=self.responsavel)
        self.client.post(self.url_inscricao, self.dados)

        self.sessao.dataHora = timezone.now() + timedelta(hours=6)
        self.sessao.save(update_fields=["dataHora"])

        resposta = self.client.delete(
            self.url_cancelamento,
            {**self.dados, "motivo": "Desistência"},
            format="json",
        )
        self.aluno.refresh_from_db()

        self.assertEqual(resposta.status_code, 204)
        self.assertEqual(self.aluno.creditos, 3)

    def test_inscricao_duplicada_nao_desconta_novamente(self):
        """Rejeita duplicidade sem consumir créditos adicionais."""
        self.client.force_authenticate(user=self.responsavel)

        self.client.post(self.url_inscricao, self.dados)
        resposta = self.client.post(self.url_inscricao, self.dados)
        self.aluno.refresh_from_db()

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(self.aluno.creditos, 3)

    def test_consultar_agendamentos(self):
        """Responsável consulta as inscrições de seus dependentes."""
        self.client.force_authenticate(user=self.responsavel)
        self.client.post(self.url_inscricao, self.dados)

        resposta = self.client.get(
            reverse("responsavel-agendamentos", args=[self.responsavel.pk])
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data), 1)
        self.assertEqual(resposta.data[0]["aluno_id"], self.aluno.pk)
        self.assertEqual(resposta.data[0]["sessao_id"], self.sessao.pk)

    def test_nao_consultar_agendamentos_outra_familia(self):
        """Impede acesso aos agendamentos de outro responsável."""
        self.client.force_authenticate(user=self.outro)

        resposta = self.client.get(
            reverse("responsavel-agendamentos", args=[self.responsavel.pk])
        )

        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_agendamentos_sem_autenticacao(self):
        """Bloqueia consultas sem autenticação."""
        resposta = self.client.get(
            reverse("responsavel-agendamentos", args=[self.responsavel.pk])
        )

        self.assertIn(resposta.status_code, [401, 403])