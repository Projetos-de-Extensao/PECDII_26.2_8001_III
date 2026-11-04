from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import RequestFactory, TestCase
from django.utils import timezone

from app.Enums import StatusPresenca, StatusSessao
from app.models import Aluno, Presenca, Sala, Sessao


class PresencaTests(TestCase):
    def setUp(self):
        self.aluno = Aluno.objects.create(
            username='aluno-presenca',
            matricula='ALU-PRES-001',
        )
        self.sala = Sala.objects.create(numero=301, capacidade=10)

    def criar_sessao(self, status=StatusSessao.CONFIRMADA):
        return Sessao.objects.create(
            sala=self.sala,
            dataHora=timezone.now(),
            duracao=timedelta(minutes=45),
            status=status,
            creditosNecessarios=0,
        )

    def criar_presenca(self, sessao=None, status=StatusPresenca.PRESENTE):
        presenca = Presenca(
            sessao=sessao or self.criar_sessao(),
            aluno=self.aluno,
            status=status,
        )
        presenca.full_clean()
        presenca.save()
        return presenca

    def test_cria_presenca_associada_a_sessao_e_aluno(self):
        sessao = self.criar_sessao()
        presenca = self.criar_presenca(sessao=sessao)

        self.assertEqual(presenca.sessao, sessao)
        self.assertEqual(presenca.aluno, self.aluno)
        self.assertEqual(presenca.status, StatusPresenca.PRESENTE)
        self.assertEqual(sessao.presencas.get(), presenca)
        self.assertEqual(self.aluno.presencas.get(), presenca)

    def test_status_deve_ser_uma_opcao_valida(self):
        presenca = Presenca(
            sessao=self.criar_sessao(),
            aluno=self.aluno,
            status='INVALIDO',
        )

        with self.assertRaises(ValidationError):
            presenca.full_clean()

        with self.assertRaises(IntegrityError), transaction.atomic():
            presenca.save()

    def test_presenca_deve_ser_unica_por_sessao_e_aluno(self):
        sessao = self.criar_sessao()
        self.criar_presenca(sessao=sessao)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Presenca.objects.create(
                sessao=sessao,
                aluno=self.aluno,
                status=StatusPresenca.AUSENTE,
            )

    def test_justificado_exige_justificativa(self):
        presenca = Presenca(
            sessao=self.criar_sessao(),
            aluno=self.aluno,
            status=StatusPresenca.JUSTIFICADO,
        )

        with self.assertRaises(ValidationError):
            presenca.full_clean()

        with self.assertRaises(IntegrityError), transaction.atomic():
            presenca.save()

        presenca.justificativa = '   '
        with self.assertRaises(IntegrityError), transaction.atomic():
            presenca.save()

        presenca.justificativa = 'Consulta médica'
        presenca.full_clean()

    def test_justificativa_e_opcional_para_outros_status(self):
        for status in (
            StatusPresenca.PRESENTE,
            StatusPresenca.AUSENTE,
            StatusPresenca.DESISTENTE,
        ):
            with self.subTest(status=status):
                presenca = Presenca(
                    sessao=self.criar_sessao(),
                    aluno=self.aluno,
                    status=status,
                )
                presenca.full_clean()

    def test_nao_permite_presenca_em_sessao_solicitada(self):
        presenca = Presenca(
            sessao=self.criar_sessao(StatusSessao.SOLICITADA),
            aluno=self.aluno,
            status=StatusPresenca.PRESENTE,
        )

        with self.assertRaises(ValidationError):
            presenca.full_clean()

    def test_permite_presenca_em_sessao_realizada(self):
        presenca = Presenca(
            sessao=self.criar_sessao(StatusSessao.REALIZADA),
            aluno=self.aluno,
            status=StatusPresenca.PRESENTE,
        )

        presenca.full_clean()

    def test_registrar_presenca_atualiza_registro_e_normaliza_justificativa(self):
        presenca = self.criar_presenca()

        presenca.registrarPresenca(
            StatusPresenca.JUSTIFICADO,
            '  Consulta médica  ',
        )
        presenca.refresh_from_db()

        self.assertEqual(presenca.status, StatusPresenca.JUSTIFICADO)
        self.assertEqual(presenca.justificativa, 'Consulta médica')

    def test_registrar_presenca_invalida_nao_altera_instancia_ou_banco(self):
        presenca = self.criar_presenca()

        with self.assertRaises(ValidationError):
            presenca.registrarPresenca(StatusPresenca.JUSTIFICADO, '   ')

        self.assertEqual(presenca.status, StatusPresenca.PRESENTE)
        self.assertEqual(presenca.justificativa, '')
        presenca.refresh_from_db()
        self.assertEqual(presenca.status, StatusPresenca.PRESENTE)

    def test_nao_permite_registrar_presenca_em_objeto_nao_persistido(self):
        presenca = Presenca(
            sessao=self.criar_sessao(),
            aluno=self.aluno,
            status=StatusPresenca.PRESENTE,
        )

        with self.assertRaises(ValidationError):
            presenca.registrarPresenca(StatusPresenca.AUSENTE, '')

    def test_presenca_impede_exclusao_de_sessao_e_aluno(self):
        presenca = self.criar_presenca()

        with self.assertRaises(IntegrityError), transaction.atomic():
            presenca.sessao.delete()

        with self.assertRaises(IntegrityError), transaction.atomic():
            presenca.aluno.delete()

    def test_admin_permite_apenas_consulta_de_presencas(self):
        request = RequestFactory().get('/admin/')
        request.user = get_user_model()(
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        presenca_admin = admin.site._registry[Presenca]

        self.assertTrue(presenca_admin.has_view_permission(request))
        self.assertFalse(presenca_admin.has_add_permission(request))
        self.assertFalse(presenca_admin.has_change_permission(request))
        self.assertFalse(presenca_admin.has_delete_permission(request))
