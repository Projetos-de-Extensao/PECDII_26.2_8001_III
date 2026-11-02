from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.models import Administrador, Sessao, Usuario
from app.permissions.administradorPermission import IsAdministrador


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