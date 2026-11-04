from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from app.models import Aluno, Laudo, Profissional, Sala, Sessao


class LaudoModelTests(TestCase):
    """
    Testa a criacao, integridade e validacoes do model Laudo no sistema PKZ Lab.
    """

    def setUp(self):
        """
        Cria os objetos base (Sala, Sessao, Aluno e Profissional)
        necessarios para testar o vinculo do Laudo.
        """
        # 1. Cria uma Sala
        self.sala = Sala.objects.create(
            numero=101,
            capacidade=10
        )

        # 2. Cria uma Sessao
        self.sessao = Sessao.objects.create(
            sala=self.sala,
            dataHora=timezone.now(),
            duracao=timedelta(minutes=60),
            creditosNecessarios=2
        )

        # 3. Cria um Aluno
        self.aluno = Aluno.objects.create(
            username="aluno_test",
            matricula="ALU-100",
            email="aluno@pkzlab.com"
        )

        # 4. Cria um Profissional
        self.profissional = Profissional.objects.create(
            username="prof_test",
            tipoContrato="CLT",
            formacao="Fisioterapia"
        )

    def test_criar_laudo_valido(self):
        """
        Verifica se um laudo com todas as chaves estrangeiras e
        o link do arquivo e criado com sucesso no banco de dados.
        """
        laudo = Laudo.objects.create(
            sessao=self.sessao,
            aluno=self.aluno,
            profissional=self.profissional,
            linkArquivo="https://storage.pkzlab.com/laudos/laudo_001.pdf"
        )

        self.assertIsNotNone(laudo.pk)
        self.assertEqual(laudo.sessao, self.sessao)
        self.assertEqual(laudo.aluno, self.aluno)
        self.assertEqual(laudo.profissional, self.profissional)
        self.assertEqual(
            laudo.linkArquivo,
            "https://storage.pkzlab.com/laudos/laudo_001.pdf"
        )
        self.assertIsNotNone(laudo.dataGeracao)

    def test_representacao_str(self):
        """
        Verifica se a representacao textual (__str__) do laudo
        retorna o formato esperado.
        """
        laudo = Laudo.objects.create(
            sessao=self.sessao,
            aluno=self.aluno,
            profissional=self.profissional,
            linkArquivo="https://storage.pkzlab.com/laudos/laudo_001.pdf"
        )

        string_esperada = f"Laudo #{laudo.pk} - Aluno: {self.aluno} (Sessão #{self.sessao.pk})"
        self.assertEqual(str(laudo), string_esperada)

    def test_link_arquivo_url_invalida(self):
        """
        Verifica se a validacao do model rejeita strings que nao
        sejam URLs validas no campo linkArquivo.
        """
        laudo = Laudo(
            sessao=self.sessao,
            aluno=self.aluno,
            profissional=self.profissional,
            linkArquivo="caminho/invalido/sem_protocolo.pdf"
        )

        with self.assertRaises(ValidationError):
            laudo.full_clean()

    def test_laudo_exige_campos_obrigatorios(self):
        """
        Verifica se a criacao de um laudo falha caso algum relacionamento
        ou campo obrigatorio esteja ausente.
        """
        laudo_sem_aluno = Laudo(
            sessao=self.sessao,
            profissional=self.profissional,
            linkArquivo="https://storage.pkzlab.com/laudos/laudo.pdf"
        )

        with self.assertRaises(ValidationError):
            laudo_sem_aluno.full_clean()

    def test_exclusao_em_cascata_sessao(self):
        """
        Verifica se o laudo e removido (CASCADE) caso a Sessao
        relacionada seja excluida.
        """
        laudo = Laudo.objects.create(
            sessao=self.sessao,
            aluno=self.aluno,
            profissional=self.profissional,
            linkArquivo="https://storage.pkzlab.com/laudos/laudo_002.pdf"
        )

        self.sessao.delete()

        self.assertFalse(
            Laudo.objects.filter(pk=laudo.pk).exists()
        )

    def test_exclusao_em_cascata_aluno(self):
        """
        Verifica se o laudo e removido (CASCADE) caso o Aluno
        relacionado seja excluido.
        """
        laudo = Laudo.objects.create(
            sessao=self.sessao,
            aluno=self.aluno,
            profissional=self.profissional,
            linkArquivo="https://storage.pkzlab.com/laudos/laudo_003.pdf"
        )

        self.aluno.delete()

        self.assertFalse(
            Laudo.objects.filter(pk=laudo.pk).exists()
        )

    def test_profissionais_laudos_emitidos_related_name(self):
        """
        Verifica se o relacionamento reverso (related_name='laudos_emitidos')
        no model Profissional funciona corretamente.
        """
        laudo = Laudo.objects.create(
            sessao=self.sessao,
            aluno=self.aluno,
            profissional=self.profissional,
            linkArquivo="https://storage.pkzlab.com/laudos/laudo_004.pdf"
        )

        self.assertIn(
            laudo,
            self.profissional.laudos_emitidos.all()
        )