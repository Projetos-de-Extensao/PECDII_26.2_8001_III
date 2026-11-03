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
            StatusSessao.REJEITADA
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


    def test_administrador_desativa_usuario(self):
        """
        Verifica se um administrador consegue
        desativar uma conta de usuário pela API.
        """

        self.autenticar_administrador()

        url = reverse(
            "administrador-desativar-usuario",
            kwargs={"usuario_id": self.usuario.pk}
        )

        response = self.client.post(url)

        # Atualiza os dados do usuário.
        self.usuario.refresh_from_db()

        # Confirma que a operação foi realizada.
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.usuario.is_active)

        # O usuário deve continuar cadastrado.
        self.assertTrue(
            Usuario.objects.filter(pk=self.usuario.pk).exists()
        )

    def test_usuario_comum_nao_desativa_usuario(self):
        """
        Verifica se um usuário comum não consegue
        desativar contas de outros usuários.
        """

        # Autentica como usuário comum.
        self.client.force_authenticate(user=self.usuario)

        url = reverse(
            "administrador-desativar-usuario",
            kwargs={"usuario_id": self.administrador.pk}
        )

        response = self.client.post(url)

        self.administrador.refresh_from_db()

        # A operação deve ser proibida.
        self.assertEqual(response.status_code, 403)

        # A conta administrativa permanece ativa.
        self.assertTrue(self.administrador.is_active)


    def test_desativar_usuario_inexistente(self):
        """
        Verifica se a API retorna HTTP 404 quando
        o usuário informado não existe.
        """

        self.autenticar_administrador()

        url = reverse(
            "administrador-desativar-usuario",
            kwargs={"usuario_id": 99999}
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)


    def test_desativar_usuario_ja_inativo(self):
        """
        Verifica se a API rejeita uma tentativa
        de desativar um usuário já desativado.
        """

        # Desativa previamente o usuário.
        self.usuario.is_active = False
        self.usuario.save(update_fields=["is_active"])

        self.autenticar_administrador()

        url = reverse(
            "administrador-desativar-usuario",
            kwargs={"usuario_id": self.usuario.pk}
        )

        response = self.client.post(url)

        # O modelo deve rejeitar a operação.
        self.assertEqual(response.status_code, 400)


    def test_administrador_cadastra_sala(self):
        """
        Verifica se um administrador consegue cadastrar
        uma sala válida pela API administrativa.
        """

        # Autentica o administrador.
        self.autenticar_administrador()

        # Obtém a URL do endpoint administrativo.
        url = reverse("administrador-cadastrar-sala")

        # Define os dados da nova sala.
        dados = {
            "numero": 105,
            "capacidade": 25
        }

        # Envia a requisição de cadastro.
        response = self.client.post(
            url,
            dados,
            format="json"
        )

        # Confirma que o cadastro foi realizado.
        self.assertEqual(response.status_code, 201)

        # Verifica se a sala foi salva no banco.
        self.assertTrue(
            Sala.objects.filter(
                numero=105,
                capacidade=25
            ).exists()
        )

    def test_cadastrar_sala_capacidade_invalida(self):
        """
        Verifica se a API impede o cadastro de salas
        com capacidade igual ou inferior a zero.
        """

        self.autenticar_administrador()

        url = reverse("administrador-cadastrar-sala")

        # Capacidade zero viola a regra do modelo Sala.
        dados = {
            "numero": 106,
            "capacidade": 0
        }

        response = self.client.post(
            url,
            dados,
            format="json"
        )

        # O cadastro deve ser rejeitado.
        self.assertEqual(response.status_code, 400)

        # Confirma que nenhuma sala inválida foi cadastrada.
        self.assertFalse(
            Sala.objects.filter(numero=106).exists()
        )

    def test_cadastrar_sala_duplicada(self):
        """
        Verifica se a API impede o cadastro de duas
        salas com o mesmo número.
        """

        self.autenticar_administrador()

        url = reverse("administrador-cadastrar-sala")

        # A sala 301 já foi criada no setUp.
        dados = {
            "numero": 301,
            "capacidade": 30
        }

        response = self.client.post(
            url,
            dados,
            format="json"
        )

        # O cadastro duplicado deve ser rejeitado.
        self.assertEqual(response.status_code, 400)

        # Deve continuar existindo somente uma sala 301.
        self.assertEqual(
            Sala.objects.filter(numero=301).count(),
            1
        )

    def test_usuario_comum_nao_cadastra_sala(self):
        """
        Verifica se usuários comuns não conseguem
        cadastrar salas pela API administrativa.
        """

        # Autentica como usuário comum.
        self.client.force_authenticate(
            user=self.usuario
        )

        url = reverse("administrador-cadastrar-sala")

        dados = {
            "numero": 107,
            "capacidade": 15
        }

        response = self.client.post(
            url,
            dados,
            format="json"
        )

        # A permissão administrativa deve bloquear o acesso.
        self.assertEqual(response.status_code, 403)

        # Confirma que a sala não foi cadastrada.
        self.assertFalse(
            Sala.objects.filter(numero=107).exists()
        )

    def test_administrador_cadastra_usuario(self):
        """
        Verifica se um administrador consegue cadastrar
        um usuário por meio da API administrativa.

        Confirma também o armazenamento seguro da senha.
        """

        self.autenticar_administrador()

        url = reverse("administrador-cadastrar-usuario")

        dados = {
            "username": "novo_usuario",
            "email": "novo@email.com",
            "password": "senhaSegura123"
        }

        response = self.client.post(
            url,
            dados,
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        # Recupera o usuário cadastrado.
        usuario = Usuario.objects.get(
            username="novo_usuario"
        )

        # Confirma que a senha foi protegida.
        self.assertTrue(
            usuario.check_password("senhaSegura123")
        )

        # A senha original não pode estar armazenada.
        self.assertNotEqual(
            usuario.password,
            "senhaSegura123"
        )

        # A senha não pode aparecer na resposta.
        self.assertNotIn(
            "password",
            response.data["usuario"]
        )

    def test_usuario_comum_nao_cadastra_usuario(self):
        """
        Verifica se usuários comuns não conseguem
        cadastrar contas pela API administrativa.
        """

        self.client.force_authenticate(
            user=self.usuario
        )

        url = reverse("administrador-cadastrar-usuario")

        dados = {
            "username": "usuario_indevido",
            "password": "senhaSegura123"
        }

        response = self.client.post(
            url,
            dados,
            format="json"
        )

        self.assertEqual(response.status_code, 403)

        self.assertFalse(
            Usuario.objects.filter(
                username="usuario_indevido"
            ).exists()
        )

    def test_cadastrar_usuario_sem_senha(self):
        """
        Verifica se a API exige uma senha
        durante o cadastro de usuários.
        """

        self.autenticar_administrador()

        url = reverse("administrador-cadastrar-usuario")

        dados = {
            "username": "usuario_sem_senha",
            "email": "teste@email.com"
        }

        response = self.client.post(
            url,
            dados,
            format="json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn(
            "password",
            response.data
        )


    def test_cadastrar_usuario_duplicado(self):
        """
        Verifica se a API impede o cadastro
        de usuários com usernames duplicados.
        """

        self.autenticar_administrador()

        url = reverse("administrador-cadastrar-usuario")

        dados = {
            "username": "usuario_api",
            "password": "senhaSegura123"
        }

        response = self.client.post(
            url,
            dados,
            format="json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            Usuario.objects.filter(
                username="usuario_api"
            ).count(),
            1
        )

    def test_cadastro_nao_concede_privilegios(self):
        """
        Verifica se campos administrativos enviados
        indevidamente no JSON não concedem privilégios.
        """

        self.autenticar_administrador()

        url = reverse("administrador-cadastrar-usuario")

        dados = {
            "username": "usuario_privilegios",
            "password": "senhaSegura123",
            "is_superuser": True,
            "is_staff": True
        }

        response = self.client.post(
            url,
            dados,
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        usuario = Usuario.objects.get(
            username="usuario_privilegios"
        )

        self.assertFalse(usuario.is_superuser)
        self.assertFalse(usuario.is_staff)