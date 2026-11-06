
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from app.Enums import StatusSessao
from app.models import (
    Profissional,
    Treinador,
    Nutricionista,
    Psicologo,
    Fisioterapeuta,
    Sala,
    Sessao,
)


class ProfissionalModelTests(TestCase):

    def setUp(self):
        self.treinador = Treinador.objects.create(
            username='treinador1',
            tipoContrato='CLT',
            formacao='Educacao Fisica',
            especialidade='Musculacao',
        )

        self.sala = Sala.objects.create(
            numero=101,
            capacidade=20,
        )

    def test_treinador_herda_dados_de_usuario(self):
        self.assertIsInstance(
            self.treinador, Profissional
        )
        self.assertEqual(
            self.treinador.username, 'treinador1'
        )
        self.assertEqual(
            self.treinador.tipoContrato, 'CLT'
        )
        self.assertEqual(
            self.treinador.formacao, 'Educacao Fisica'
        )
        self.assertEqual(
            self.treinador.especialidade, 'Musculacao'
        )

    def test_subclasses_possuem_atributos(self):
        nutricionista = Nutricionista.objects.create(
            username='nutri1',
            tipoContrato='PJ',
            formacao='Nutricao',
            CRN='12345',
        )

        psicologo = Psicologo.objects.create(
            username='psico1',
            tipoContrato='CLT',
            formacao='Psicologia',
            CRP='54321',
        )

        fisioterapeuta = Fisioterapeuta.objects.create(
            username='fisio1',
            tipoContrato='PJ',
            formacao='Fisioterapia',
            CREFITO='98765',
        )

        self.assertEqual(nutricionista.CRN, '12345')
        self.assertEqual(psicologo.CRP, '54321')
        self.assertEqual(fisioterapeuta.CREFITO, '98765')

    def test_solicitar_sessao(self):
        sessao = self.treinador.solicitarSessao(
            sala=self.sala,
            dataHora=timezone.now(),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
        )

        self.assertIsInstance(sessao, Sessao)
        self.assertEqual(sessao.sala, self.sala)
        self.assertEqual(
            sessao.status, StatusSessao.SOLICITADA
        )
        self.assertEqual(sessao.creditosNecessarios, 2)

    def test_solicitar_sessao_com_sala_invalida(self):
        with self.assertRaises(ValidationError):
            self.treinador.solicitarSessao(
                sala=None,
                dataHora=timezone.now(),
                duracao=timedelta(hours=1),
                creditosNecessarios=2,
            )

    def test_solicitar_sessao_com_duracao_invalida(self):
        with self.assertRaises(ValidationError):
            self.treinador.solicitarSessao(
                sala=self.sala,
                dataHora=timezone.now(),
                duracao=timedelta(0),
                creditosNecessarios=2,
            )

    def test_cancelar_sessao(self):
        sessao = self.treinador.solicitarSessao(
            sala=self.sala,
            dataHora=timezone.now() + timedelta(days=1),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
        )

        self.treinador.cancelarSessao(
            sessao, 'Indisponibilidade'
        )

        sessao.refresh_from_db()

        self.assertEqual(
            sessao.status, StatusSessao.CANCELADA
        )
        self.assertEqual(
            sessao.motivoCancelamento,
            'Indisponibilidade'
        )

    def test_cancelar_sessao_sem_motivo(self):
        sessao = self.treinador.solicitarSessao(
            sala=self.sala,
            dataHora=timezone.now(),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
        )

        with self.assertRaises(ValidationError):
            self.treinador.cancelarSessao(sessao, '')
