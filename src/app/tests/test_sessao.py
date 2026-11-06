from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from app.Enums import StatusSessao
from app.models import Sala, Sessao
from app.models import Aluno, Presenca, Sala, Sessao


class SessaoTests(TestCase):
    def criar_sessao(self, **campos):
        sala = Sala.objects.create(numero=101, capacidade=20)
        dados = {
            'sala': sala,
            'dataHora': timezone.now() + timedelta(days=1),
            'duracao': timedelta(minutes=60),
            'creditosNecessarios': 1,
        }
        dados.update(campos)
        return Sessao.objects.create(**dados)

    def test_cria_sessao_com_estado_inicial_e_sala(self):
        sessao = self.criar_sessao()

        self.assertEqual(sessao.status, StatusSessao.SOLICITADA)
        self.assertEqual(sessao.sala.numero, 101)
        self.assertEqual(sessao.motivoCancelamento, '')

    def test_duracao_deve_ser_positiva(self):
        sessao = Sessao(
            sala=Sala.objects.create(numero=101, capacidade=20),
            dataHora=timezone.now(),
            duracao=timedelta(0),
            creditosNecessarios=0,
        )

        with self.assertRaises(ValidationError):
            sessao.full_clean()

        with self.assertRaises(IntegrityError), transaction.atomic():
            sessao.save()

    def test_creditos_nao_podem_ser_negativos(self):
        sessao = Sessao(
            sala=Sala.objects.create(numero=101, capacidade=20),
            dataHora=timezone.now(),
            duracao=timedelta(minutes=30),
            creditosNecessarios=-1,
        )

        with self.assertRaises(ValidationError):
            sessao.full_clean()

        with self.assertRaises(IntegrityError), transaction.atomic():
            sessao.save()

    def test_status_deve_ser_uma_opcao_valida(self):
        sessao = Sessao(
            sala=Sala.objects.create(numero=101, capacidade=20),
            dataHora=timezone.now(),
            duracao=timedelta(minutes=30),
            creditosNecessarios=0,
            status='INVALIDO',
        )

        with self.assertRaises(ValidationError):
            sessao.full_clean()

    def test_cancela_sessao_solicitada_e_persiste_motivo(self):
        sessao = self.criar_sessao()

        sessao.cancelar('  Solicitação do responsável  ')
        sessao.refresh_from_db()

        self.assertEqual(sessao.status, StatusSessao.CANCELADA)
        self.assertEqual(sessao.motivoCancelamento, 'Solicitação do responsável')

    def test_cancela_sessao_confirmada(self):
        sessao = self.criar_sessao()
        Sessao.objects.filter(pk=sessao.pk).update(status=StatusSessao.CONFIRMADA)
        sessao.refresh_from_db()

        sessao.cancelar('Cancelamento confirmado')

        self.assertEqual(sessao.status, StatusSessao.CANCELADA)

    def test_cancelamento_exige_motivo_nao_vazio(self):
        sessao = self.criar_sessao()

        for motivo in ('   ', None):
            with self.subTest(motivo=motivo):
                with self.assertRaises(ValidationError):
                    sessao.cancelar(motivo)

        sessao.refresh_from_db()
        self.assertEqual(sessao.status, StatusSessao.SOLICITADA)

    def test_nao_cancela_sessao_realizada_ou_ja_cancelada(self):
        sessao = self.criar_sessao()

        for status in (StatusSessao.REALIZADA, StatusSessao.CANCELADA):
            with self.subTest(status=status):
                Sessao.objects.filter(pk=sessao.pk).update(status=status)
                sessao.refresh_from_db()

                with self.assertRaises(ValidationError):
                    sessao.cancelar('Motivo')


    
    def test_cancelamento_reembolsa_todos(self):
        """Devolve integralmente os créditos de todos os inscritos."""
        sessao = self.criar_sessao(
            status=StatusSessao.CONFIRMADA,
            creditosNecessarios=2,
        )
        alunos = [
            Aluno.objects.create_user(
                username=f"aluno_reembolso_{i}",
                password="Senha123!",
                matricula=f"REEMB-{i}",
                creditos=5,
            )
            for i in range(2)
        ]

        for aluno in alunos:
            sessao.inscreverAluno(aluno)

        sessao.cancelar("Indisponibilidade do estabelecimento")

        for aluno in alunos:
            aluno.refresh_from_db()
            self.assertEqual(aluno.creditos, 5)

    def test_cancelamento_repetido_nao_reembolsa(self):
        """Impede que a mesma sessão seja reembolsada duas vezes."""
        sessao = self.criar_sessao(
            status=StatusSessao.CONFIRMADA,
            creditosNecessarios=2,
        )
        aluno = Aluno.objects.create_user(
            username="aluno_repetido",
            password="Senha123!",
            matricula="REEMB-REP",
            creditos=5,
        )
        sessao.inscreverAluno(aluno)
        sessao.cancelar("Cancelamento")

        with self.assertRaises(ValidationError):
            sessao.cancelar("Novo cancelamento")

        aluno.refresh_from_db()
        self.assertEqual(aluno.creditos, 5)

    def test_cancelamento_preserva_presencas(self):
        """Mantém os registros dos inscritos após o cancelamento."""
        sessao = self.criar_sessao(
            status=StatusSessao.CONFIRMADA,
            creditosNecessarios=2,
        )
        aluno = Aluno.objects.create_user(
            username="aluno_historico",
            password="Senha123!",
            matricula="REEMB-HIST",
            creditos=5,
        )
        sessao.inscreverAluno(aluno)
        sessao.cancelar("Cancelamento")

        self.assertTrue(
            Presenca.objects.filter(sessao=sessao, aluno=aluno).exists()
        )

    def test_cancelamento_sem_inscritos_nao_gera_creditos(self):
        """Cancela uma sessão solicitada sem gerar reembolsos."""
        sessao = self.criar_sessao()

        sessao.cancelar("Sessão indisponível")
        sessao.refresh_from_db()

        self.assertEqual(sessao.status, StatusSessao.CANCELADA)
        self.assertFalse(Presenca.objects.filter(sessao=sessao).exists())

    def test_cancelamento_altera_status_das_presencas(self):
        """Cancela as inscrições sem excluir os registros."""
        sessao = self.criar_sessao(
            status=StatusSessao.CONFIRMADA,
            creditosNecessarios=2,
        )
        aluno = Aluno.objects.create_user(
            username="aluno_status_cancelado",
            password="Senha123!",
            matricula="CANC-STATUS",
            creditos=5,
        )

        presenca = sessao.inscreverAluno(aluno)

        self.assertEqual(presenca.status, "PENDENTE")

        sessao.cancelar("Indisponibilidade da sala")

        presenca.refresh_from_db()
        aluno.refresh_from_db()

        self.assertEqual(presenca.status, "CANCELADA")
        self.assertEqual(aluno.creditos, 5)
        self.assertTrue(Presenca.objects.filter(pk=presenca.pk).exists())

    def test_reinscricao_apos_desistencia(self):
        """Permite reinscrição sem duplicar o registro."""
        sessao = self.criar_sessao(
            status=StatusSessao.CONFIRMADA,
            creditosNecessarios=2,
        )
        aluno = Aluno.objects.create_user(
            username="aluno_reinscricao",
            password="Senha123!",
            matricula="REINS-01",
            creditos=5,
        )

        sessao.inscreverAluno(aluno)
        sessao.removerAluno(aluno)
        sessao.inscreverAluno(aluno)

        aluno.refresh_from_db()
        presenca = Presenca.objects.get(sessao=sessao, aluno=aluno)

        self.assertEqual(aluno.creditos, 3)
        self.assertEqual(presenca.status, "PENDENTE")
        self.assertEqual(Presenca.objects.filter(sessao=sessao, aluno=aluno).count(), 1)    

    def test_desistencia_duplicada_nao_reembolsa(self):
        """Uma inscrição não pode ser cancelada duas vezes."""
        sessao = self.criar_sessao(
            status=StatusSessao.CONFIRMADA,
            creditosNecessarios=2,
        )
        aluno = Aluno.objects.create_user(
            username="aluno_dupla_desistencia",
            password="Senha123!",
            matricula="DESIST-01",
            creditos=5,
        )

        sessao.inscreverAluno(aluno)
        sessao.removerAluno(aluno)

        with self.assertRaises(ValidationError):
            sessao.removerAluno(aluno)

        aluno.refresh_from_db()
        self.assertEqual(aluno.creditos, 5)

    def test_cancelamento_nao_reembolsa_desistente(self):
        """Reembolsa somente alunos com inscrição ativa."""
        sessao = self.criar_sessao(
            status=StatusSessao.CONFIRMADA,
            creditosNecessarios=2,
        )
        aluno = Aluno.objects.create_user(
            username="aluno_desistente_cancelamento",
            password="Senha123!",
            matricula="DESIST-02",
            creditos=5,
        )

        sessao.inscreverAluno(aluno)
        sessao.removerAluno(aluno)
        sessao.cancelar("Indisponibilidade da sala")

        aluno.refresh_from_db()
        presenca = Presenca.objects.get(sessao=sessao, aluno=aluno)

        self.assertEqual(aluno.creditos, 5)
        self.assertEqual(presenca.status, "DESISTENTE")
