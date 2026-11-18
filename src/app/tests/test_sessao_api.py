from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import (
    Administrador,
    Aluno,
    Presenca,
    Responsavel,
    Sala,
    Sessao,
    Treinador,
    Usuario,
)
from app.Enums import StatusSessao
from app.models.responsavelModel import VinculoResponsavel


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

    def test_nao_permite_solicitar_sessoes_sobrepostas_na_mesma_sala(self):
        """Impede sobreposição de sessões solicitadas na mesma sala."""
        data_hora = timezone.now() + timedelta(days=2)
        dados = {**self.dados, "dataHora": data_hora.isoformat()}

        primeira = self.client.post(reverse("sessao-list"), dados)
        segunda = self.client.post(
            reverse("sessao-list"),
            {
                **dados,
                "dataHora": (data_hora + timedelta(minutes=30)).isoformat(),
            },
        )

        self.assertEqual(primeira.status_code, status.HTTP_201_CREATED)
        self.assertEqual(segunda.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("conflitante", str(segunda.data))
        self.assertEqual(Sessao.objects.count(), 1)

    def test_permite_sessoes_adjacentes_ou_em_salas_diferentes(self):
        """Permite sessões adjacentes e horários iguais em salas diferentes."""
        data_hora = timezone.now() + timedelta(days=2)
        dados = {**self.dados, "dataHora": data_hora.isoformat()}
        primeira = self.client.post(reverse("sessao-list"), dados)

        adjacente = self.client.post(
            reverse("sessao-list"),
            {
                **dados,
                "dataHora": (data_hora + timedelta(hours=1)).isoformat(),
            },
        )
        outra_sala = Sala.objects.create(numero=102, capacidade=20)
        outro_profissional = Treinador.objects.create(
            username="treinador_sala_diferente",
            tipoContrato="CLT",
            formacao="Educacao Fisica",
            especialidade="Natacao",
        )
        self.client.force_authenticate(user=outro_profissional)
        mesmo_horario = self.client.post(
            reverse("sessao-list"),
            {**dados, "sala": outra_sala.pk},
        )

        self.assertEqual(primeira.status_code, status.HTTP_201_CREATED)
        self.assertEqual(adjacente.status_code, status.HTTP_201_CREATED)
        self.assertEqual(mesmo_horario.status_code, status.HTTP_201_CREATED)

    def test_sessao_rejeitada_libera_horario_da_sala(self):
        """Sessões rejeitadas não reservam mais a sala."""
        primeira = self.client.post(reverse("sessao-list"), self.dados)
        Sessao.objects.filter(pk=primeira.data["id"]).update(
            status=StatusSessao.REJEITADA
        )

        segunda = self.client.post(reverse("sessao-list"), self.dados)

        self.assertEqual(segunda.status_code, status.HTTP_201_CREATED)

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

        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_profissional_nao_pode_agendar_conflito_em_outra_sala(self):
        data_hora = timezone.now() + timedelta(days=4)
        primeira_sala = Sala.objects.create(numero=103, capacidade=20)
        outra_sala = Sala.objects.create(numero=104, capacidade=20)
        primeira = Sessao.solicitar(
            self.profissional,
            primeira_sala,
            data_hora,
            timedelta(hours=1),
            2,
        )
        resposta = self.client.post(
            reverse("sessao-list"),
            {
                **self.dados,
                "sala": outra_sala.pk,
                "dataHora": (data_hora + timedelta(minutes=30)).isoformat(),
            },
        )

        self.assertEqual(primeira.status, StatusSessao.SOLICITADA)
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profissional", resposta.data["erro"][0])
        self.assertEqual(Sessao.objects.count(), 1)

    def test_profissional_lista_apenas_suas_sessoes_e_detalhe_alheio_retorna_404(self):
        sessao_propria = self.criar_sessao()
        outro_profissional = Treinador.objects.create(
            username="treinador_privado",
            tipoContrato="CLT",
            formacao="Educacao Fisica",
            especialidade="Natacao",
        )
        outra_sala = Sala.objects.create(numero=105, capacidade=10)
        sessao_alheia = Sessao.objects.create(
            sala=outra_sala,
            profissional=outro_profissional,
            dataHora=timezone.now() + timedelta(days=4),
            duracao=timedelta(hours=1),
            creditosNecessarios=1,
        )

        resposta_lista = self.client.get(reverse("sessao-list"))
        resposta_detalhe = self.client.get(
            reverse("sessao-detail", args=[sessao_alheia.pk])
        )

        self.assertEqual(resposta_lista.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [sessao["id"] for sessao in resposta_lista.data],
            [sessao_propria.pk],
        )
        self.assertEqual(
            resposta_detalhe.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_responsavel_lista_somente_sessoes_de_dependentes(self):
        responsavel = Responsavel.objects.create_user(
            username="responsavel_sessoes",
            password="Senha123!",
        )
        aluno = Aluno.objects.create_user(
            username="aluno_sessoes",
            password="Senha123!",
            matricula="ALU-SESS-01",
        )
        VinculoResponsavel.objects.create(
            responsavel=responsavel,
            aluno=aluno,
        )
        sessao_vinculada = Sessao.objects.create(
            sala=self.sala,
            profissional=self.profissional,
            dataHora=timezone.now() + timedelta(days=5),
            duracao=timedelta(hours=1),
            creditosNecessarios=1,
            status=StatusSessao.CONFIRMADA,
        )
        Presenca.objects.create(
            sessao=sessao_vinculada,
            aluno=aluno,
            status="PENDENTE",
        )
        sessao_sem_dependente = Sessao.objects.create(
            sala=Sala.objects.create(numero=106, capacidade=10),
            profissional=self.profissional,
            dataHora=timezone.now() + timedelta(days=6),
            duracao=timedelta(hours=1),
            creditosNecessarios=1,
            status=StatusSessao.CONFIRMADA,
        )
        self.client.force_authenticate(user=responsavel)

        resposta = self.client.get(reverse("sessao-list"))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [sessao["id"] for sessao in resposta.data],
            [sessao_vinculada.pk],
        )
        self.assertNotEqual(sessao_vinculada.pk, sessao_sem_dependente.pk)

    def test_usuario_generico_nao_lista_sessoes(self):
        usuario = Usuario.objects.create_user(
            username="usuario_sem_perfil",
            password="Senha123!",
        )
        sessao = self.criar_sessao()
        self.client.force_authenticate(user=usuario)

        resposta_lista = self.client.get(reverse("sessao-list"))
        resposta_detalhe = self.client.get(
            reverse("sessao-detail", args=[sessao.pk])
        )

        self.assertEqual(resposta_lista.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta_lista.data, [])
        self.assertEqual(
            resposta_detalhe.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_patch_generico_nao_altera_sessao(self):
        sessao = self.criar_sessao()

        resposta = self.client.patch(
            reverse("sessao-detail", args=[sessao.pk]),
            {"status": StatusSessao.CANCELADA},
        )

        self.assertEqual(
            resposta.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        sessao.refresh_from_db()
        self.assertEqual(sessao.status, StatusSessao.SOLICITADA)

    def test_administrador_lista_sessoes_de_todos_os_profissionais(self):
        sessao_propria = self.criar_sessao()
        outro_profissional = Treinador.objects.create(
            username="treinador_admin_sessoes",
            tipoContrato="CLT",
            formacao="Educacao Fisica",
            especialidade="Natacao",
        )
        sessao_alheia = Sessao.objects.create(
            sala=Sala.objects.create(numero=107, capacidade=10),
            profissional=outro_profissional,
            dataHora=timezone.now() + timedelta(days=7),
            duracao=timedelta(hours=1),
            creditosNecessarios=1,
        )
        self.client.force_authenticate(user=self.admin)

        resposta = self.client.get(reverse("sessao-list"))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {sessao["id"] for sessao in resposta.data},
            {sessao_propria.pk, sessao_alheia.pk},
        )