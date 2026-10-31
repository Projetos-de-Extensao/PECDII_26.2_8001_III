from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from app.models import Aluno, TipoResponsavel


class AlunoModelTests(TestCase):
    def test_aluno_herda_dados_de_usuario(self):
        aluno = Aluno.objects.create(
            username='aluno',
            first_name='Ana',
            email='ana@example.com',
            matricula='ALU-001',
        )

        self.assertEqual(aluno.first_name, 'Ana')
        self.assertEqual(aluno.email, 'ana@example.com')
        self.assertEqual(aluno.responsavel, TipoResponsavel.NENHUM)
        self.assertEqual(aluno.creditos, 0)

    def test_matricula_deve_ser_unica(self):
        Aluno.objects.create(username='aluno1', matricula='ALU-001')

        with self.assertRaises(IntegrityError), transaction.atomic():
            Aluno.objects.create(username='aluno2', matricula='ALU-001')

    def test_creditos_nao_aceitam_valor_negativo(self):
        aluno = Aluno(
            username='aluno',
            matricula='ALU-001',
            creditos=-1,
        )

        with self.assertRaises(ValidationError):
            aluno.full_clean()

    def test_assumir_tutoria_define_responsavel_proprio(self):
        aluno = Aluno.objects.create(
            username='aluno',
            matricula='ALU-001',
            responsavel=TipoResponsavel.TUTOR,
        )

        aluno.assumirTutoria()
        aluno.refresh_from_db()

        self.assertEqual(aluno.responsavel, TipoResponsavel.PROPRIO)

    def test_responsavel_deve_ser_uma_opcao_valida(self):
        aluno = Aluno(
            username='aluno',
            matricula='ALU-001',
            responsavel='INVALIDO',
        )

        with self.assertRaises(ValidationError):
            aluno.full_clean()
