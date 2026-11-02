from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient

from app.Enums import StatusSessao
from app.models import Administrador, Usuario, Sala, Sessao


class AdministradorAPITests(TestCase):
    """
    Testa os endpoints administrativos de aprovação
    e desaprovação de sessões.

    Verifica autenticação, autorização, validações
    e alterações persistidas no banco de dados.
    """

    def setUp(self):
        """
        Prepara os usuários, a sala e o cliente HTTP
        utilizados nos testes.
        """

        # Cria uma conta administrativa.
        self.administrador = Administrador.objects.create_user(
            username="admin_api",
            password="senha123",
            tipoContrato="CLT"
        )

        # Cria uma conta comum, sem privilégios administrativos.
        self.usuario = Usuario.objects.create_user(
            username="usuario_api",
            password="senha123"
        )

        # Cria a sala utilizada pelas sessões.
        self.sala = Sala.objects.create(
            numero=301,
            capacidade=20
        )

        # Cliente HTTP utilizado para simular requisições.
        self.client = APIClient()

    def criar_sessao(self):
        """
        Cria uma sessão válida no estado SOLICITADA.

        Returns:
            Sessao: Sessão cadastrada no banco de testes.
        """

        return Sessao.objects.create(
            sala=self.sala,
            dataHora=timezone.now(),
            duracao=timedelta(hours=1),
            creditosNecessarios=1
        )

    def autenticar_administrador(self):
        """
        Autentica o cliente de testes como administrador.
        """

        self.client.force_authenticate(
            user=self.administrador
        )

    def test_administrador_aprova_sessao(self):
        """
        Verifica se um administrador consegue aprovar
        uma sessão solicitada pela API.
        """

        sessao = self.criar_sessao()
        self.autenticar_administrador()

        # Obtém a URL pelo nome registrado no router.
        url = reverse(
            "administrador-aprovar-sessao",
            kwargs={"sessao_id": sessao.pk}
        )

        response = self.client.post(url)

        sessao.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sessao.status,
            StatusSessao.CONFIRMADA
        )

    def test_administrador_desaprova_sessao(self):
        """
        Verifica se a desaprovação registra o motivo
        e altera o status da sessão.
        """

        sessao = self.criar_sessao()
        self.autenticar_administrador()

        url = reverse(
            "administrador-desaprovar-sessao",
            kwargs={"sessao_id": sessao.pk}
        )

        response = self.client.post(
            url,
            {"motivo": "Sala indisponível"},
            format="json"
        )

        sessao.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sessao.status,
            StatusSessao.CANCELADA
        )
        self.assertEqual(
            sessao.motivoCancelamento,
            "Sala indisponível"
        )

    def test_usuario_comum_nao_aprova_sessao(self):
        """
        Verifica se usuários comuns não conseguem
        aprovar sessões pela API.
        """

        sessao = self.criar_sessao()

        # Autentica como usuário comum.
        self.client.force_authenticate(user=self.usuario)

        url = reverse(
            "administrador-aprovar-sessao",
            kwargs={"sessao_id": sessao.pk}
        )

        response = self.client.post(url)

        sessao.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            sessao.status,
            StatusSessao.SOLICITADA
        )

    def test_usuario_anonimo_nao_aprova_sessao(self):
        """
        Verifica se requisições não autenticadas
        são bloqueadas pela API.
        """

        sessao = self.criar_sessao()

        url = reverse(
            "administrador-aprovar-sessao",
            kwargs={"sessao_id": sessao.pk}
        )

        response = self.client.post(url)

        self.assertIn(response.status_code, [401, 403])

        sessao.refresh_from_db()

        self.assertEqual(
            sessao.status,
            StatusSessao.SOLICITADA
        )

    def test_aprovar_sessao_inexistente(self):
        """
        Verifica se a API retorna HTTP 404 quando
        o identificador da sessão não existe.
        """

        self.autenticar_administrador()

        url = reverse(
            "administrador-aprovar-sessao",
            kwargs={"sessao_id": 99999}
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

    def test_aprovar_sessao_ja_confirmada(self):
        """
        Verifica se a API impede a aprovação
        de uma sessão que já foi confirmada.
        """

        sessao = self.criar_sessao()

        sessao.status = StatusSessao.CONFIRMADA
        sessao.save(update_fields=["status"])

        self.autenticar_administrador()

        url = reverse(
            "administrador-aprovar-sessao",
            kwargs={"sessao_id": sessao.pk}
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)

    def test_desaprovar_sessao_sem_motivo(self):
        """
        Verifica se a API exige uma justificativa
        para desaprovar uma sessão.
        """

        sessao = self.criar_sessao()
        self.autenticar_administrador()

        url = reverse(
            "administrador-desaprovar-sessao",
            kwargs={"sessao_id": sessao.pk}
        )

        response = self.client.post(
            url,
            {},
            format="json"
        )

        sessao.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            sessao.status,
            StatusSessao.SOLICITADA
        )

    def test_desaprovar_sessao_realizada(self):
        """
        Verifica se uma sessão realizada não pode
        ser desaprovada pela API.
        """

        sessao = self.criar_sessao()

        sessao.status = StatusSessao.REALIZADA
        sessao.save(update_fields=["status"])

        self.autenticar_administrador()

        url = reverse(
            "administrador-desaprovar-sessao",
            kwargs={"sessao_id": sessao.pk}
        )

        response = self.client.post(
            url,
            {"motivo": "Solicitação inválida"},
            format="json"
        )

        sessao.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            sessao.status,
            StatusSessao.REALIZADA
        )