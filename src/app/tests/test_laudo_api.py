from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from app.models import (
    Administrador, Aluno, Laudo, Presenca,
    Responsavel, Sala, Sessao, Treinador,
)
from app.models.responsavelModel import VinculoResponsavel
from app.Enums import StatusPresenca


class TestesLaudoAPI(APITestCase):
    """Testa emissão, validações, permissões e download de laudos."""

    def setUp(self):
        self.admin = Administrador.objects.create(
            username="admin_laudo",
        )

        self.treinador = Treinador.objects.create(
            username="treinador_laudo",
            tipoContrato="CLT",
            formacao="Educação Física",
            especialidade="Futebol",
        )

        self.outro = Treinador.objects.create(
            username="outro_treinador_laudo",
            tipoContrato="CLT",
            formacao="Educação Física",
            especialidade="Futebol",
        )

        self.responsavel = Responsavel.objects.create(
            username="responsavel_laudo",
        )

        self.outro_responsavel = Responsavel.objects.create(
            username="outro_responsavel_laudo",
        )

        self.aluno = Aluno.objects.create(
            username="aluno_laudo",
            matricula="LAUDO-001",
        )

        VinculoResponsavel.objects.create(
            responsavel=self.responsavel,
            aluno=self.aluno,
        )

        self.sala = Sala.objects.create(
            numero=801,
            capacidade=20,
        )

        self.sessao = Sessao.solicitar(
            profissional=self.treinador,
            sala=self.sala,
            dataHora=timezone.now() + timedelta(days=2),
            duracao=timedelta(hours=1),
            creditosNecessarios=0,
        )

        self.sessao.confirmar()

        self.presenca = Presenca.novaPresenca(
            self.sessao,
            self.aluno,
        )

        self.url = "/api/laudos/"

        self.dados = {
            "sessao": self.sessao.pk,
            "aluno": self.aluno.pk,
            "tipoDocumento": "DESEMPENHO",
            "conteudo": {
                "desempenhoFisico": "Bom desempenho.",
                "evolucao": "Melhora na resistência.",
                "recomendacoes": "Manter os treinos.",
            },
        }

    def criar_laudo(self):
        """Cria um laudo válido para os testes de consulta."""
        return Laudo.objects.create(
            sessao=self.sessao,
            aluno=self.aluno,
            profissional=self.treinador,
            tipoDocumento="DESEMPENHO",
            conteudo=self.dados["conteudo"],
        )

    def test_criar_laudo_valido(self):
        self.client.force_authenticate(user=self.treinador)

        resposta = self.client.post(
            self.url, self.dados, format="json"
        )

        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(Laudo.objects.count(), 1)
        self.assertEqual(
            resposta.data["profissional"],
            self.treinador.pk,
        )

    def test_documento_incompativel(self):
        self.client.force_authenticate(user=self.treinador)

        dados = self.dados.copy()
        dados["tipoDocumento"] = "PSICOLOGIA"

        resposta = self.client.post(
            self.url, dados, format="json"
        )

        self.assertEqual(resposta.status_code, 400)

    def test_campos_obrigatorios(self):
        self.client.force_authenticate(user=self.treinador)

        dados = self.dados.copy()
        dados["conteudo"] = {"evolucao": "Boa evolução."}

        resposta = self.client.post(
            self.url, dados, format="json"
        )

        self.assertEqual(resposta.status_code, 400)

    def test_aluno_sem_inscricao(self):
        self.client.force_authenticate(user=self.treinador)

        self.presenca.delete()

        resposta = self.client.post(
            self.url, self.dados, format="json"
        )

        self.assertEqual(resposta.status_code, 400)

    def test_inscricao_cancelada_ou_desistente(self):
        self.client.force_authenticate(user=self.treinador)

        for situacao in (
            StatusPresenca.CANCELADA,
            StatusPresenca.DESISTENTE,
        ):
            self.presenca.status = situacao
            self.presenca.save(update_fields=["status"])

            resposta = self.client.post(
                self.url, self.dados, format="json"
            )

            self.assertEqual(resposta.status_code, 400)

    def test_outro_profissional_nao_pode_emitir(self):
        self.client.force_authenticate(user=self.outro)

        resposta = self.client.post(
            self.url, self.dados, format="json"
        )

        self.assertEqual(resposta.status_code, 403)

    def test_responsavel_nao_pode_emitir(self):
        self.client.force_authenticate(user=self.responsavel)

        resposta = self.client.post(
            self.url, self.dados, format="json"
        )

        self.assertEqual(resposta.status_code, 403)

    def test_consulta_por_responsavel(self):
        laudo = self.criar_laudo()

        self.client.force_authenticate(user=self.responsavel)

        resposta = self.client.get(f"{self.url}{laudo.pk}/")

        self.assertEqual(resposta.status_code, 200)

        self.client.force_authenticate(
            user=self.outro_responsavel
        )

        resposta = self.client.get(f"{self.url}{laudo.pk}/")

        self.assertEqual(resposta.status_code, 404)

    def test_administrador_pode_consultar(self):
        laudo = self.criar_laudo()

        self.client.force_authenticate(user=self.admin)

        resposta = self.client.get(f"{self.url}{laudo.pk}/")

        self.assertEqual(resposta.status_code, 200)

    def test_download_pdf(self):
        laudo = self.criar_laudo()

        self.client.force_authenticate(user=self.treinador)

        resposta = self.client.get(
            f"{self.url}{laudo.pk}/pdf/"
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta["Content-Type"],
            "application/pdf",
        )

        conteudo = b"".join(resposta.streaming_content)

        self.assertTrue(conteudo.startswith(b"%PDF-"))
        resposta.close()

    def test_pdf_sem_permissao(self):
        laudo = self.criar_laudo()

        self.client.force_authenticate(
            user=self.outro_responsavel
        )

        resposta = self.client.get(
            f"{self.url}{laudo.pk}/pdf/"
        )

        self.assertEqual(resposta.status_code, 404)

    def test_usuario_nao_autenticado(self):
        resposta = self.client.get(self.url)

        self.assertEqual(resposta.status_code, 401)