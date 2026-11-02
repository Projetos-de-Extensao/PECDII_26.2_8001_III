from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView
from rest_framework.response import Response

from app.models import Usuario, Administrador
from app.permissions.administradorPermission import IsAdministrador


class ViewAdministrativaTeste(APIView):
    """
    View utilizada exclusivamente para testar
    a permissão administrativa.

    Simula um endpoint protegido, sem alterar
    as views existentes no projeto.
    """

    permission_classes = [IsAdministrador]

    def get(self, request):
        """
        Retorna uma resposta de sucesso quando
        o usuário possui autorização administrativa.
        """

        return Response({"mensagem": "Acesso autorizado"})


class AdministradorPermissionTests(TestCase):
    """
    Testa o controle de acesso administrativo.

    Verifica o comportamento da permissão para
    administradores, usuários comuns, contas
    desativadas e requisições anônimas.
    """

    def setUp(self):
        """
        Prepara os usuários e a view utilizados
        nos testes de autorização.
        """

        # Cria um administrador válido.
        self.administrador = Administrador.objects.create_user(
            username="admin_permissao",
            password="senha123",
            tipoContrato="CLT"
        )

        # Cria um usuário comum, sem privilégios administrativos.
        self.usuario = Usuario.objects.create_user(
            username="usuario_comum",
            password="senha123"
        )

        # Prepara a criação de requisições HTTP.
        self.factory = APIRequestFactory()

        # Converte a classe de teste em uma view executável.
        self.view = ViewAdministrativaTeste.as_view()

    def test_administrador_tem_acesso(self):
        """
        Verifica se um administrador autenticado
        consegue acessar uma operação protegida.
        """

        # Cria uma requisição HTTP.
        request = self.factory.get("/teste-administrador/")

        # Autentica a requisição como administrador.
        force_authenticate(request, user=self.administrador)

        # Executa a view protegida.
        response = self.view(request)

        # Confirma que o acesso foi autorizado.
        self.assertEqual(response.status_code, 200)

    def test_usuario_comum_nao_tem_acesso(self):
        """
        Verifica se um usuário comum não consegue
        executar operações administrativas.
        """

        request = self.factory.get("/teste-administrador/")

        # Autentica como usuário comum.
        force_authenticate(request, user=self.usuario)

        response = self.view(request)

        # Confirma que o acesso foi negado.
        self.assertEqual(response.status_code, 403)

    def test_usuario_anonimo_nao_tem_acesso(self):
        """
        Verifica se uma requisição sem autenticação
        não consegue acessar operações administrativas.
        """

        # Não autentica nenhum usuário.
        request = self.factory.get("/teste-administrador/")

        response = self.view(request)

        # A API deve impedir o acesso.
        # Dependendo da autenticação configurada,
        # o DRF pode retornar 401 ou 403.
        self.assertIn(response.status_code, [401, 403])

    def test_administrador_desativado_nao_tem_acesso(self):
        """
        Verifica se uma conta administrativa desativada
        perde a autorização para executar operações.
        """

        # Desativa o administrador.
        self.administrador.is_active = False
        self.administrador.save(update_fields=["is_active"])

        request = self.factory.get("/teste-administrador/")

        # Simula uma requisição com o usuário desativado.
        force_authenticate(request, user=self.administrador)

        response = self.view(request)

        # Confirma que o acesso foi negado.
        self.assertEqual(response.status_code, 403)