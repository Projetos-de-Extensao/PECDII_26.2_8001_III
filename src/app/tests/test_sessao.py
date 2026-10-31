from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from app.Enums import StatusSessao
from app.models import Sala, Sessao


class SessaoTests(TestCase):
    def criar_sessao(self, **campos):
        sala = Sala.objects.create(numero=101, capacidade=20)
        dados = {
            'sala': sala,
            'dataHora': timezone.now(),
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
