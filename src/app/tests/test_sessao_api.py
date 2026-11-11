from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import Administrador, Treinador, Sala, Sessao
from app.Enums import StatusSessao


class TestesSessaoAPI(APITestCase):
    """Testa as operações e permissões da API de Sessão."""

    def setUp(self):
        self.admin = Administrador.objects.create(
            username="admin_sessao",
            tipoContrato="CLT",
        )
        self.profissional = Treinador.objects.create(
            username="treinador_sessao",
            tipoContrato="CLT",
            formacao="Educacao Fisica",
            especialidade="Futebol",
        )
        self.sala = Sala.objects.create(numero=101, capacidade=20)

        self.dados = {
            "sala": self.sala.pk,
            "dataHora": (
                timezone.now() + timedelta(days=2)
            ).isoformat(),
            "duracao": "01:00:00",
            "creditosNecessarios": 2,
        }

        self.client.force_authenticate(user=self.profissional)

    def criar_sessao(self):
        """Cria uma sessão solicitada para os testes."""
        return Sessao.solicitar(
            profissional=self.profissional,
            sala=self.sala,
            dataHora=timezone.now() + timedelta(days=2),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
        )

    def test_profissional_solicita_sessao(self):
        """Profissional pode solicitar sua própria sessão."""
        resposta = self.client.post(
            reverse("sessao-list"), self.dados
        )

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            resposta.data["status"], StatusSessao.SOLICITADA
        )

    def test_nao_permite_solicitar_sessao_com_data_passada(self):
        """Impede agendar uma sessão para uma data que já passou."""
        dados = {
            **self.dados,
            "dataHora": (
                timezone.now() - timedelta(days=1)
            ).isoformat(),
        }

        resposta = self.client.post(reverse("sessao-list"), dados)

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resposta.data["erro"],
            ["A data e hora da sessão devem ser futuras."],
        )
        self.assertEqual(Sessao.objects.count(), 0)

    def test_administrador_solicita_sessao(self):
        """Administrador pode solicitar em nome do profissional."""
        self.client.force_authenticate(user=self.admin)

        dados = {
            **self.dados,
            "profissional": self.profissional.pk,
        }

        resposta = self.client.post(reverse("sessao-list"), dados)

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)

    def test_administrador_confirma_sessao(self):
        """Administrador confirma uma sessão solicitada."""
        sessao = self.criar_sessao()
        self.client.force_authenticate(user=self.admin)

        resposta = self.client.post(
            reverse("sessao-confirmar", args=[sessao.pk])
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resposta.data["status"], StatusSessao.CONFIRMADA
        )

    def test_administrador_rejeita_sessao(self):
        """Administrador rejeita uma sessão com justificativa."""
        sessao = self.criar_sessao()
        self.client.force_authenticate(user=self.admin)

        resposta = self.client.post(
            reverse("sessao-rejeitar", args=[sessao.pk]),
            {"motivo": "Sala indisponível"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resposta.data["status"], StatusSessao.REJEITADA
        )
        self.assertEqual(
            resposta.data["motivoCancelamento"],
            "Sala indisponível",
        )

    def test_profissional_cancela_propria_sessao(self):
        """Profissional cancela uma sessão sob sua responsabilidade."""
        sessao = self.criar_sessao()

        resposta = self.client.post(
            reverse("sessao-cancelar", args=[sessao.pk]),
            {"motivo": "Indisponibilidade"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resposta.data["status"], StatusSessao.CANCELADA
        )

    def test_sem_autenticacao(self):
        """Bloqueia acesso à API sem autenticação."""
        self.client.force_authenticate(user=None)

        resposta = self.client.get(reverse("sessao-list"))

        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profissional_nao_confirma_sessao(self):
        """Profissional não pode confirmar sessões."""
        sessao = self.criar_sessao()

        resposta = self.client.post(
            reverse("sessao-confirmar", args=[sessao.pk])
        )

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_profissional_nao_rejeita_sessao(self):
        """Profissional não pode rejeitar sessões."""
        sessao = self.criar_sessao()

        resposta = self.client.post(
            reverse("sessao-rejeitar", args=[sessao.pk]),
            {"motivo": "Teste"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrador_precisa_informar_profissional(self):
        """Administrador deve identificar o profissional da sessão."""
        self.client.force_authenticate(user=self.admin)

        resposta = self.client.post(reverse("sessao-list"), self.dados)

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profissional_nao_cancela_sessao_alheia(self):
        """Impede cancelar sessão de outro profissional."""
        outro = Treinador.objects.create(
            username="outro_treinador",
            tipoContrato="CLT",
            formacao="Educacao Fisica",
            especialidade="Natacao",
        )

        sessao = Sessao.solicitar(
            profissional=outro,
            sala=self.sala,
            dataHora=timezone.now() + timedelta(days=3),
            duracao=timedelta(hours=1),
            creditosNecessarios=2,
        )

        resposta = self.client.post(
            reverse("sessao-cancelar", args=[sessao.pk]),
            {"motivo": "Teste"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_filtro_por_profissional(self):
        """Filtra sessões pelo profissional informado."""
        sessao = self.criar_sessao()

        resposta = self.client.get(
            reverse("sessao-list"),
            {"profissional": self.profissional.pk},
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data), 1)
        self.assertEqual(resposta.data[0]["id"], sessao.pk)

    def test_filtro_invalido(self):
        """Rejeita filtros com valores inválidos."""
        resposta = self.client.get(
            reverse("sessao-list"),
            {"profissional": "abc"},
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)