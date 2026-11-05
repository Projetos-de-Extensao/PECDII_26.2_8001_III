"""Testes de inscrição de dependentes em sessões pelo responsável."""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from app.Enums import StatusSessao
from app.models import Aluno, Presenca, Profissional, Responsavel, Sala, Sessao
from app.models.responsavelModel import VinculoResponsavel


class TestesInscricaoResponsavel(TestCase):
    """Valida a integração entre responsável, aluno, sessão e presença."""

    def setUp(self):
        """Prepara dependente com créditos e sessão confirmada."""
        self.responsavel = Responsavel.objects.create_user(
            username="responsavel_inscricao", password="SenhaSegura123!"
        )
        self.outro_responsavel = Responsavel.objects.create_user(
            username="outro_responsavel", password="SenhaSegura123!"
        )
        self.aluno = Aluno.objects.create_user(
            username="aluno_inscricao", password="SenhaSegura123!",
            matricula="MAT-INSCRICAO-001", creditos=5,
        )
        VinculoResponsavel.objects.create(responsavel=self.responsavel, aluno=self.aluno)
        self.sala = Sala.objects.create(numero=101, capacidade=10)
        self.profissional = Profissional.objects.create_user(
            username="profissional_inscricao", password="SenhaSegura123!",
            tipoContrato="CLT", formacao="Educação Física",
        )
        self.sessao = Sessao.objects.create(
            sala=self.sala,
            profissional=self.profissional,
            dataHora=timezone.now() + timedelta(days=1),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
            status=StatusSessao.CONFIRMADA,
        )

    def test_inscrever_dependente(self):
        """Inscrição válida cria uma presença associada ao dependente."""
        self.responsavel.inscreverDependenteEmSessao(self.aluno, self.sessao)
        self.assertTrue(Presenca.objects.filter(sessao=self.sessao, aluno=self.aluno).exists())

    def test_impedir_inscricao_por_outro_responsavel(self):
        """Responsável sem vínculo não pode inscrever o aluno."""
        with self.assertRaises(ValidationError):
            self.outro_responsavel.inscreverDependenteEmSessao(self.aluno, self.sessao)
        self.assertFalse(Presenca.objects.filter(sessao=self.sessao, aluno=self.aluno).exists())

    def test_cancelar_inscricao(self):
        """Cancelamento válido remove a presença sem cancelar a sessão."""
        self.responsavel.inscreverDependenteEmSessao(self.aluno, self.sessao)
        self.responsavel.cancelarInscricaoDependenteEmSessao(
            self.aluno, self.sessao, "Solicitação do responsável"
        )
        self.assertFalse(Presenca.objects.filter(sessao=self.sessao, aluno=self.aluno).exists())
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.status, StatusSessao.CONFIRMADA)

    def test_impedir_cancelamento_por_outro_responsavel(self):
        """Responsável sem vínculo não pode cancelar a inscrição."""
        self.responsavel.inscreverDependenteEmSessao(self.aluno, self.sessao)
        with self.assertRaises(ValidationError):
            self.outro_responsavel.cancelarInscricaoDependenteEmSessao(
                self.aluno, self.sessao, "Cancelamento indevido"
            )
        self.assertTrue(Presenca.objects.filter(sessao=self.sessao, aluno=self.aluno).exists())

    def test_cancelamento_sem_motivo(self):
        """Cancelamento exige um motivo não vazio."""
        self.responsavel.inscreverDependenteEmSessao(self.aluno, self.sessao)
        with self.assertRaises(ValidationError):
            self.responsavel.cancelarInscricaoDependenteEmSessao(
                self.aluno, self.sessao, "   "
            )
        self.assertTrue(Presenca.objects.filter(sessao=self.sessao, aluno=self.aluno).exists())
