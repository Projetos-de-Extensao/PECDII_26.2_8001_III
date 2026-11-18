from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from app.Enums import StatusPresenca
from app.models import Administrador, Aluno, Presenca, Sala, Sessao, Treinador


class TestesCreditosPresencasAPI(APITestCase):
    """Testa créditos, presença e permissões."""

    def setUp(self):
        self.admin = Administrador.objects.create(username="admin_teste")
        self.treinador = Treinador.objects.create(
            username="treinador_teste",
            tipoContrato="CLT",
            formacao="Educação Física",
            especialidade="Futebol",
        )
        self.outro = Treinador.objects.create(
            username="outro_treinador",
            tipoContrato="CLT",
            formacao="Educação Física",
            especialidade="Futebol",
        )
        self.aluno = Aluno.objects.create(
            username="aluno_teste",
            matricula="MAT-TESTE-001",
        )
        sala = Sala.objects.create(numero=999, capacidade=20)
        self.sessao = Sessao.objects.create(
            profissional=self.treinador,
            sala=sala,
            dataHora=timezone.now() - timedelta(days=2),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
            status="CONFIRMADA",
        )
        self.presenca = Presenca.novaPresenca(self.sessao, self.aluno)

        self.url_creditos = reverse(
            "administrador-gerenciar-creditos",
            kwargs={"aluno_id": self.aluno.pk},
        )
        self.url_presenca = reverse(
            "sessao-registrar-presenca",
            kwargs={"pk": self.sessao.pk, "aluno_id": self.aluno.pk},
        )
        self.url_lista = reverse(
            "sessao-listar-presencas",
            kwargs={"pk": self.sessao.pk},
        )

    def test_adicionar_remover_creditos(self):
        self.client.force_authenticate(user=self.admin)

        for quantidade, saldo in [(10, 10), (-3, 7)]:
            resposta = self.client.patch(
                self.url_creditos, {"quantidade": quantidade}, format="json"
            )
            self.assertEqual(resposta.status_code, 200)
            self.aluno.refresh_from_db()
            self.assertEqual(self.aluno.creditos, saldo)

    def test_creditos_insuficientes(self):
        self.client.force_authenticate(user=self.admin)
        resposta = self.client.patch(
            self.url_creditos, {"quantidade": -1}
        )
        self.assertEqual(resposta.status_code, 400)

    def test_creditos_sem_permissao(self):
        self.client.force_authenticate(user=self.treinador)
        resposta = self.client.patch(
            self.url_creditos, {"quantidade": 10}
        )
        self.assertEqual(resposta.status_code, 403)

    def test_registrar_presencas(self):
        self.client.force_authenticate(user=self.treinador)

        for situacao in (
            StatusPresenca.PRESENTE,
            StatusPresenca.AUSENTE,
            StatusPresenca.JUSTIFICADO,
        ):
            resposta = self.client.patch(
                self.url_presenca,
                {"status": situacao, "justificativa": "Atestado médico."},
            )
            self.assertEqual(resposta.status_code, 200)
            self.presenca.refresh_from_db()
            self.assertEqual(self.presenca.status, situacao)

    def test_listar_presencas(self):
        self.client.force_authenticate(user=self.treinador)
        resposta = self.client.get(self.url_lista)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.data), 1)
        self.assertEqual(resposta.data[0]["aluno_id"], self.aluno.pk)

    def test_outro_treinador_sem_permissao(self):
        self.client.force_authenticate(user=self.outro)

        resposta = self.client.patch(
            self.url_presenca, {"status": StatusPresenca.PRESENTE}
        )
        self.assertEqual(resposta.status_code, 404)

        resposta = self.client.get(self.url_lista)
        self.assertEqual(resposta.status_code, 404)

    def test_realizar_sessao(self):
        """Somente o treinador responsável pode concluir a sessão."""
        url = reverse("sessao-realizar", kwargs={"pk": self.sessao.pk})

        self.client.force_authenticate(user=self.outro)
        self.assertEqual(self.client.post(url).status_code, 404)

        self.client.force_authenticate(user=self.treinador)
        resposta = self.client.post(url)

        self.assertEqual(resposta.status_code, 200)
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.status, "REALIZADA")

        # Impede concluir novamente.
        self.assertEqual(self.client.post(url).status_code, 400)

    def test_nao_realiza_sessao_antes_do_horario_de_termino(self):
        sessao_futura = Sessao.objects.create(
            sala=Sala.objects.create(numero=1000, capacidade=20),
            profissional=self.treinador,
            dataHora=timezone.now() + timedelta(days=2),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
            status="CONFIRMADA",
        )
        self.client.force_authenticate(user=self.treinador)

        resposta = self.client.post(
            reverse("sessao-realizar", kwargs={"pk": sessao_futura.pk})
        )

        self.assertEqual(resposta.status_code, 400)
        sessao_futura.refresh_from_db()
        self.assertEqual(sessao_futura.status, "CONFIRMADA")

    def test_presenca_recusa_inscricao_desistente_sem_alterar_o_status(self):
        self.presenca.status = StatusPresenca.DESISTENTE
        self.presenca.save(update_fields=["status"])
        self.client.force_authenticate(user=self.treinador)

        resposta = self.client.patch(
            self.url_presenca,
            {"status": StatusPresenca.PRESENTE},
        )

        self.assertEqual(resposta.status_code, 400)
        self.presenca.refresh_from_db()
        self.assertEqual(self.presenca.status, StatusPresenca.DESISTENTE)

    def test_presenca_nao_pode_ser_lancada_antes_do_inicio(self):
        sessao_futura = Sessao.objects.create(
            sala=Sala.objects.create(numero=1001, capacidade=20),
            profissional=self.treinador,
            dataHora=timezone.now() + timedelta(days=2),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
            status="CONFIRMADA",
        )
        presenca_futura = Presenca.novaPresenca(sessao_futura, self.aluno)
        self.client.force_authenticate(user=self.treinador)

        resposta = self.client.patch(
            reverse(
                "sessao-registrar-presenca",
                kwargs={
                    "pk": sessao_futura.pk,
                    "aluno_id": self.aluno.pk,
                },
            ),
            {"status": StatusPresenca.PRESENTE},
        )

        self.assertEqual(resposta.status_code, 400)
        presenca_futura.refresh_from_db()
        self.assertEqual(presenca_futura.status, StatusPresenca.PENDENTE)