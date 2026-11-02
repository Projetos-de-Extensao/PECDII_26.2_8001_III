from django.core.exceptions import ValidationError
from django.test import TestCase

from app.models import Administrador, Usuario
from app.models import Administrador, Usuario, Sala

from datetime import timedelta

from django.utils import timezone

from app.Enums import StatusSessao
from app.models import Sessao


class AdministradorTests(TestCase):
    """
    Testa as funcionalidades da classe Administrador.

    Verifica a criação de administradores e as operações
    administrativas relacionadas à gestão de usuários.
    """

    def setUp(self):
        """
        Cria um administrador para utilização nos testes.

        O Django utiliza um banco de dados de teste separado,
        preservando os registros do banco principal.
        """

        self.administrador = Administrador(
            username="admin",
            tipoContrato="CLT"
        )

        self.administrador.set_password("senha-segura")
        self.administrador.save()

    def criar_sessao(self):
        """
        Cria uma sessão válida para os testes administrativos.

        A sessão é associada a uma sala cadastrada e
        recebe automaticamente o status SOLICITADA.

        Returns:
            Sessao: Instância cadastrada no banco de testes.
        """

        # Cria a sala necessária para realizar a sessão.
        sala = Sala.objects.create(
            numero=201,
            capacidade=20
        )

        # Cria uma sessão com os campos obrigatórios.
        sessao = Sessao.objects.create(
            sala=sala,
            dataHora=timezone.now(),
            duracao=timedelta(minutes=60),
            creditosNecessarios=1
        )

        return sessao

    def test_criar_administrador(self):
        """
        Verifica se o administrador é criado corretamente.

        Confirma o atributo específico tipoContrato
        e a herança dos atributos da classe Usuario.
        """

        self.assertEqual(
            self.administrador.tipoContrato,
            "CLT"
        )

        self.assertEqual(
            self.administrador.username,
            "admin"
        )

        self.assertIsInstance(
            self.administrador,
            Usuario
        )

    def test_cadastrar_usuario(self):
        """
        Verifica se o administrador consegue cadastrar
        um novo usuário no banco de dados.
        """

        usuario = Usuario(
            username="joao",
            email="joao@email.com"
        )

        usuario.set_password("senha123")

        self.administrador.cadastrarUsuario(usuario)

        self.assertTrue(
            Usuario.objects.filter(username="joao").exists()
        )

    def test_desativar_usuario(self):
        """
        Verifica se o administrador consegue desativar
        um usuário sem excluir seu registro.
        """

        usuario = Usuario.objects.create_user(
            username="maria",
            password="senha123"
        )

        self.administrador.desativarUsuario(usuario)

        usuario.refresh_from_db()

        self.assertFalse(usuario.is_active)

        self.assertTrue(
            Usuario.objects.filter(pk=usuario.pk).exists()
        )


    def test_cadastrar_sala(self):
        """
        Verifica se o administrador consegue cadastrar
        uma sala válida no sistema PKZ Lab.

        O teste confirma que a sala foi registrada
        corretamente no banco de dados.
        """

        # Cria uma instância de Sala ainda não cadastrada.
        sala = Sala(
            numero=101,
            capacidade=20
        )

        # Executa o método administrativo de cadastro.
        self.administrador.cadastrarSala(sala)

        # Verifica se a sala foi registrada no banco.
        self.assertTrue(
            Sala.objects.filter(numero=101).exists()
        )

        # Confirma que os atributos foram preservados.
        self.assertEqual(sala.capacidade, 20)


    def test_cadastrar_sala_capacidade_invalida(self):
        """
        Verifica se o administrador não consegue cadastrar
        uma sala com capacidade menor que 1.

        O método cadastrarSala deve executar as
        validações existentes no modelo Sala.
        """

        # Cria uma sala com capacidade inválida.
        sala = Sala(
            numero=102,
            capacidade=0
        )

        # Verifica se o cadastro gera um erro de validação.
        with self.assertRaises(ValidationError):
            self.administrador.cadastrarSala(sala)

        # Confirma que a sala não foi cadastrada.
        self.assertFalse(
            Sala.objects.filter(numero=102).exists()
        )

    def test_cadastrar_sala_duplicada(self):
        """
        Verifica se o administrador não consegue cadastrar
        duas salas com o mesmo número.

        O teste garante que a restrição de unicidade
        definida no modelo Sala seja respeitada.
        """

        # Cadastra uma sala válida.
        Sala.objects.create(
            numero=103,
            capacidade=20
        )

        # Tenta cadastrar outra sala com o mesmo número.
        sala_duplicada = Sala(
            numero=103,
            capacidade=30
        )

        # Verifica se o cadastro duplicado é rejeitado.
        with self.assertRaises(ValidationError):
            self.administrador.cadastrarSala(sala_duplicada)

        # Confirma que apenas uma sala possui esse número.
        self.assertEqual(
            Sala.objects.filter(numero=103).count(),
            1
        )


    def test_aprovar_sessao(self):
        """
        Verifica se o administrador consegue aprovar
        uma sessão que está aguardando confirmação.
        """

        # Cria uma sessão inicialmente solicitada.
        sessao = self.criar_sessao()

        # Executa a aprovação administrativa.
        self.administrador.aprovarSessao(sessao)

        # Atualiza os dados da sessão a partir do banco.
        sessao.refresh_from_db()

        # Confirma que a sessão foi aprovada.
        self.assertEqual(
            sessao.status,
            StatusSessao.CONFIRMADA
        )

    def test_aprovar_sessao_ja_confirmada(self):
        """
        Verifica se o administrador não consegue aprovar
        novamente uma sessão que já está confirmada.
        """

        sessao = self.criar_sessao()

        # Realiza a primeira aprovação.
        self.administrador.aprovarSessao(sessao)

        # Uma segunda aprovação deve ser rejeitada.
        with self.assertRaises(ValidationError):
            self.administrador.aprovarSessao(sessao)

        sessao.refresh_from_db()

        # O status deve permanecer confirmado.
        self.assertEqual(
            sessao.status,
            StatusSessao.CONFIRMADA
        )

    def test_desaprovar_sessao(self):
        """
        Verifica se o administrador consegue desaprovar
        uma sessão solicitada, registrando o motivo.

        A desaprovação utiliza o cancelamento existente
        no modelo Sessao.
        """

        sessao = self.criar_sessao()

        motivo = "Horário indisponível"

        # Executa a desaprovação administrativa.
        self.administrador.desaprovarSessao(
            sessao,
            motivo
        )

        sessao.refresh_from_db()

        # Verifica o status após a desaprovação.
        self.assertEqual(
            sessao.status,
            StatusSessao.CANCELADA
        )

        # Confirma que a justificativa foi armazenada.
        self.assertEqual(
            sessao.motivoCancelamento,
            motivo
        )

    def test_desaprovar_sessao_sem_motivo(self):
        """
        Verifica se uma sessão não pode ser desaprovada
        sem uma justificativa válida.
        """

        sessao = self.criar_sessao()

        # Tenta desaprovar sem informar uma justificativa.
        with self.assertRaises(ValidationError):
            self.administrador.desaprovarSessao(
                sessao,
                ""
            )

        sessao.refresh_from_db()

        # Confirma que a sessão permanece solicitada.
        self.assertEqual(
            sessao.status,
            StatusSessao.SOLICITADA
        )

    def test_desaprovar_sessao_realizada(self):
        """
        Verifica se uma sessão já realizada não pode
        ser desaprovada pelo administrador.
        """

        sessao = self.criar_sessao()

        # Simula uma sessão que já foi realizada.
        sessao.status = StatusSessao.REALIZADA
        sessao.save(update_fields=["status"])

        # A desaprovação deve ser rejeitada.
        with self.assertRaises(ValidationError):
            self.administrador.desaprovarSessao(
                sessao,
                "Solicitação inválida"
            )

        sessao.refresh_from_db()

        # Confirma que o estado original foi preservado.
        self.assertEqual(
            sessao.status,
            StatusSessao.REALIZADA
        )