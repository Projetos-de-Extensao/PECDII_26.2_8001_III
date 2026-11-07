from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.models import Administrador, Sessao, Usuario, Sala, Aluno
from app.serializers import UsuarioSerializer, SalaSerializer
from app.permissions.administradorPermission import IsAdministrador
from app.serializers.profissionalSerializer import CadastroProfissionalSerializer
from app.models import Responsavel
from app.serializers.responsavelSerializer import ResponsavelSerializer
from app.serializers.alunoSerializer import AlunoSerializer

class AdministradorView(ViewSet):
    """
    Disponibiliza operações administrativas do PKZ Lab.

    A view utiliza os métodos já implementados no
    modelo Administrador, evitando duplicação das
    regras de negócio.

    Somente administradores autenticados e ativos
    podem acessar os endpoints desta classe.
    """

    permission_classes = [IsAdministrador]

    def obter_administrador(self, request):
        """
        Recupera o administrador associado ao usuário autenticado.

        Returns:
            Administrador: Instância do administrador autenticado.
        """

        return Administrador.objects.get(pk=request.user.pk)

    @action(
        detail=False,
        methods=["post"],
        url_path=r"sessoes/(?P<sessao_id>[0-9]+)/aprovar"
    )
    def aprovar_sessao(self, request, sessao_id=None):
        """
        Aprova uma sessão que está aguardando confirmação.

        A operação utiliza o método aprovarSessao()
        definido no modelo Administrador.
        """

        # Recupera a sessão solicitada ou retorna HTTP 404.
        from django.shortcuts import get_object_or_404

        sessao = get_object_or_404(Sessao, pk=sessao_id)

        # Recupera o administrador autenticado.
        administrador = self.obter_administrador(request)

        try:
            # Executa a regra de negócio do modelo.
            administrador.aprovarSessao(sessao)

        except ValidationError as erro:
            # Retorna HTTP 400 quando a aprovação é inválida.
            return Response(
                {"erro": erro.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Confirma a aprovação da sessão.
        return Response(
            {
                "mensagem": "Sessão aprovada com sucesso.",
                "sessao_id": sessao.pk,
                "status": sessao.status
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=["post"],
        url_path=r"sessoes/(?P<sessao_id>[0-9]+)/desaprovar"
    )
    def desaprovar_sessao(self, request, sessao_id=None):
        """
        Desaprova uma sessão solicitada.

        A operação exige uma justificativa e utiliza
        o método desaprovarSessao() do administrador.
        """

        # Recupera a sessão solicitada ou retorna HTTP 404.
        from django.shortcuts import get_object_or_404

        sessao = get_object_or_404(Sessao, pk=sessao_id)

        # Obtém a justificativa enviada na requisição.
        motivo = request.data.get("motivo")

        # Recupera o administrador autenticado.
        administrador = self.obter_administrador(request)

        try:
            # Executa a desaprovação utilizando a regra do modelo.
            administrador.desaprovarSessao(sessao, motivo)

        except ValidationError as erro:
            # Retorna HTTP 400 quando a operação é inválida.
            return Response(
                {"erro": erro.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Confirma a desaprovação.
        return Response(
            {
                "mensagem": "Sessão desaprovada com sucesso.",
                "sessao_id": sessao.pk,
                "status": sessao.status,
                "motivo": sessao.motivoCancelamento
            },
            status=status.HTTP_200_OK
        )


    @action(
        detail=False,
        methods=["post"],
        url_path=r"usuarios/(?P<usuario_id>[0-9]+)/desativar"
    )
    def desativar_usuario(self, request, usuario_id=None):
        """
        Desativa uma conta de usuário do PKZ Lab.

        Somente administradores autenticados podem
        executar esta operação.

        A desativação utiliza o método desativarUsuario()
        do modelo Administrador, preservando o registro
        do usuário no banco de dados.

        Args:
            request: Requisição HTTP recebida.
            usuario_id: Identificador do usuário a desativar.

        Returns:
            Response: Resultado da operação administrativa.
        """

        # Localiza o usuário informado na requisição.
        # Retorna HTTP 404 caso ele não exista.
        usuario = get_object_or_404(
            Usuario,
            pk=usuario_id
        )

        # Recupera o administrador autenticado.
        administrador = self.obter_administrador(request)

        try:
            # Executa a regra de negócio existente no modelo.
            administrador.desativarUsuario(usuario)

        except ValidationError as erro:
            # Retorna HTTP 400 quando a desativação é inválida.
            return Response(
                {"erro": erro.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Confirma que o usuário foi desativado.
        return Response(
            {
                "mensagem": "Usuário desativado com sucesso.",
                "usuario_id": usuario.pk,
                "is_active": usuario.is_active
            },
            status=status.HTTP_200_OK
        )


    @action(
        detail=False,
        methods=["post"],
        url_path="salas"
    )
    def cadastrar_sala(self, request):
        """
        Cadastra uma nova sala no sistema PKZ Lab.

        Somente administradores autenticados e ativos
        podem executar esta operação.

        Utiliza SalaSerializer para validar os dados
        recebidos e Administrador.cadastrarSala()
        para realizar o cadastro no banco de dados.

        Args:
            request: Requisição HTTP contendo os dados da sala.

        Returns:
            Response: Dados da sala cadastrada ou erros
            de validação.
        """

        # Valida os dados recebidos utilizando o serializer existente.
        serializer = SalaSerializer(data=request.data)

        # Retorna HTTP 400 caso os dados sejam inválidos.
        serializer.is_valid(raise_exception=True)

        # Cria uma instância de Sala sem salvá-la no banco.
        sala = Sala(**serializer.validated_data)

        # Recupera o administrador autenticado.
        administrador = self.obter_administrador(request)

        try:
            # Executa a regra de negócio definida no modelo.
            administrador.cadastrarSala(sala)

        except ValidationError as erro:
            # Retorna HTTP 400 quando o cadastro é inválido.
            return Response(
                {"erro": erro.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retorna os dados da sala cadastrada.
        return Response(
            {
                "mensagem": "Sala cadastrada com sucesso.",
                "sala": SalaSerializer(sala).data
            },
            status=status.HTTP_201_CREATED
        )


    @action(
        detail=False,
        methods=["post"],
        url_path="usuarios"
    )
    
    @action(detail=False, methods=["post"], url_path="usuarios")
    def cadastrar_usuario(self, request):
        """Cadastra usuários, profissionais e responsáveis com dependentes."""
        tipo = request.data.get("tipo")
        tipos_profissionais = (
            "treinador", "fisioterapeuta", "psicologo", "nutricionista"
        )

        if tipo is not None and tipo not in (*tipos_profissionais, "responsavel"):
            return Response(
                {"tipo": "Especialização inválida."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tipo == "responsavel":
            dados = request.data.copy()
            dados.pop("tipo", None)
            alunos = dados.pop("alunos", [])
            dados.pop("password", None)

            if not dados.get("email", "").strip():
                return Response(
                    {"email": "O e-mail do responsável é obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not isinstance(alunos, list) or not alunos:
                return Response(
                    {"alunos": "Informe pelo menos um aluno."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Evita que um aluno seja vinculado a dois responsáveis.
            if any(
                not isinstance(aluno, dict)
                or "responsavel_id" in aluno
                or "novo_responsavel" in aluno
                for aluno in alunos
            ):
                return Response(
                    {"alunos": "Não informe outro responsável nos dados dos alunos."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ResponsavelSerializer(data=dados)
            serializer.is_valid(raise_exception=True)

            serializer_alunos = AlunoSerializer(data=alunos, many=True)
            serializer_alunos.is_valid(raise_exception=True)

            # Cria todos os registros ou desfaz a operação em caso de erro.
            with transaction.atomic():
                responsavel = serializer.save()

                for aluno in serializer_alunos.save():
                    responsavel.adicionarDependente(aluno)

            # Gera o convite para definição da senha.
            uid = urlsafe_base64_encode(force_bytes(responsavel.pk))
            token = default_token_generator.make_token(responsavel)
            link = (
                "http://127.0.0.1:8000/api/usuarios/ativar-conta/"
                f"?uid={uid}&token={token}"
            )

            send_mail(
                subject="PKZ Lab - Ativação de conta",
                message=(
                    f"Olá, {responsavel.first_name or responsavel.username}!\n\n"
                    "Seu cadastro no PKZ Lab foi realizado.\n"
                    "Acesse o link abaixo para definir sua senha:\n\n"
                    f"{link}\n\n"
                    "Se você não reconhece este cadastro, ignore esta mensagem."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[responsavel.email],
                fail_silently=False,
            )

            return Response(
                {
                    "mensagem": "Responsável cadastrado. Convite enviado.",
                    "usuario": ResponsavelSerializer(responsavel).data,
                },
                status=status.HTTP_201_CREATED,
            )

        if tipo in tipos_profissionais:
            serializer = CadastroProfissionalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            profissional = serializer.save()

            return Response(
                {
                    "mensagem": "Profissional cadastrado com sucesso.",
                    "usuario": UsuarioSerializer(profissional).data,
                },
                status=status.HTTP_201_CREATED,
            )

        serializer = UsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dados = serializer.validated_data.copy()
        senha = dados.pop("password")
        usuario = Usuario(**dados)
        usuario.set_password(senha)

        try:
            self.obter_administrador(request).cadastrarUsuario(usuario)
        except ValidationError as erro:
            return Response(
                {"erro": erro.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "mensagem": "Usuário cadastrado com sucesso.",
                "usuario": UsuarioSerializer(usuario).data,
            },
            status=status.HTTP_201_CREATED,
        )


    @action(
        detail=False,
        methods=["patch"],
        url_path=r"alunos/(?P<aluno_id>[0-9]+)/creditos"
    )
    def gerenciar_creditos(self, request, aluno_id=None):
        """Adiciona ou remove créditos de um aluno."""
        aluno = get_object_or_404(Aluno, pk=aluno_id)

        quantidade = request.data.get("quantidade")

        if type(quantidade) is not int or quantidade == 0:
            return Response(
                {"erro": "Informe uma quantidade inteira diferente de zero."},
                status=status.HTTP_400_BAD_REQUEST
            )

        novo_saldo = aluno.creditos + quantidade

        if novo_saldo < 0:
            return Response(
                {"erro": "O aluno não possui créditos suficientes."},
                status=status.HTTP_400_BAD_REQUEST
            )

        aluno.creditos = novo_saldo
        aluno.save(update_fields=["creditos"])

        return Response({
            "mensagem": "Créditos atualizados com sucesso.",
            "aluno_id": aluno.pk,
            "creditos": aluno.creditos
        })